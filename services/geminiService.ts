import { GoogleGenAI } from '@google/genai';
import { VerificationResult, Verdict, EntityType } from '../types';

const getClient = () => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    throw new Error('API_KEY environment variable is missing.');
  }
  return new GoogleGenAI({ apiKey });
};

// Helper to convert file to Base64
export const fileToGenerativePart = async (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      // Remove data url prefix (e.g. "data:image/jpeg;base64,")
      const base64Data = base64String.split(',')[1];
      resolve(base64Data);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export const verifyTextClaim = async (
  text: string
): Promise<VerificationResult> => {
  const ai = getClient();
  const prompt = `
    Verify the following news headline or claim for accuracy.
    CLAIM: "${text}"
    
    INSTRUCTIONS:
    1. Use Google Search to check if this is a verified news story, a rumor, or misinformation.
    2. Determine a verdict (SAFE, SUSPICIOUS, SCAM).
    3. Assign a risk score (0-100).
    4. Provide a very brief 1-sentence summary.
    5. List any specific entities found (people, orgs) and evidence points.
    
    OUTPUT JSON:
    {
      "verdict": "SAFE" | "SUSPICIOUS" | "SCAM",
      "riskScore": number,
      "summary": "string",
      "entities": [{"type": "ORGANIZATION" | "Other", "value": "name", "verificationStatus": "status", "isFlagged": boolean}],
      "evidencePoints": ["string"],
      "recommendation": "string"
    }
    Return RAW JSON only.
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: { text: prompt },
      config: {
        tools: [{ googleSearch: {} }],
        temperature: 0.1,
      },
    });

    const responseText = response.text || '{}';
    let cleanJson = responseText;
    const jsonMatch =
      responseText.match(/```json\n([\s\S]*?)\n```/) ||
      responseText.match(/```([\s\S]*?)```/);
    if (jsonMatch) cleanJson = jsonMatch[1];
    else {
      const first = responseText.indexOf('{');
      const last = responseText.lastIndexOf('}');
      if (first !== -1 && last !== -1)
        cleanJson = responseText.substring(first, last + 1);
    }

    let data;
    try {
      data = JSON.parse(cleanJson);
    } catch (e) {
      console.error('JSON Parse Error', e);
      data = {};
    }

    // Extract grounding sources if available (Same logic as analyzeFlyer)
    const sources: Array<{ title: string; uri: string }> = [];
    if (response.candidates?.[0]?.groundingMetadata?.groundingChunks) {
      response.candidates[0].groundingMetadata.groundingChunks.forEach(
        (chunk: any) => {
          if (chunk.web?.uri) {
            sources.push({
              title: chunk.web.title || 'Web Source',
              uri: chunk.web.uri,
            });
          }
        }
      );
    }

    return {
      verdict: (data.verdict as Verdict) || Verdict.SAFE,
      riskScore: data.riskScore || 0,
      summary: data.summary || 'Verified news source.',
      entities: Array.isArray(data.entities)
        ? data.entities.map((e: any) => ({
            type: EntityType.ORGANIZATION,
            value: e.value || 'Unknown',
            verificationStatus: e.verificationStatus || 'Analyzed',
            isFlagged: !!e.isFlagged,
          }))
        : [],
      evidencePoints: Array.isArray(data.evidencePoints)
        ? data.evidencePoints
        : [],
      recommendation: data.recommendation || 'Check official sources.',
      sources: sources,
    };
  } catch (error) {
    console.error('Verification failed', error);
    return {
      verdict: Verdict.SAFE,
      riskScore: 0,
      summary: 'Unable to verify automatically due to connection error.',
      entities: [],
      evidencePoints: [],
      recommendation: 'Please try again later.',
      sources: [],
    };
  }
};

export const analyzeFlyer = async (
  base64Image: string,
  mimeType: string
): Promise<VerificationResult> => {
  const ai = getClient();

  const prompt = `
    Act as a Forensic Disaster Relief Analyst. Your job is to verify the legitimacy of the "Call for Help" flyer or image provided.
    
    PERFORM THE FOLLOWING STEPS:
    1. EXTRACT: Identify all phone numbers, URLs, email addresses, organization names, and crypto wallet addresses from the image.
    2. INVESTIGATE: Use the Google Search tool to verify these entities. 
       - Check if the organization exists and is a registered non-profit/NGO.
       - Check if the phone numbers or URLs are reported in scam databases.
       - specific queries: "is [domain] legit", "[phone number] scam report", "[org name] official site".
    3. ANALYZE: specific indicators of fraud (urgency, poor grammar, requesting crypto/gift cards, mismatching domains).
    4. REPORT: Return a JSON object with your findings.

    OUTPUT FORMAT:
    You MUST return the result in a raw JSON code block. Do not include markdown formatting like \`\`\`json.
    
    The JSON structure must be:
    {
      "riskScore": number (0-100, where 100 is definite scam),
      "verdict": "SAFE" | "SUSPICIOUS" | "SCAM",
      "summary": "A short executive summary of the investigation.",
      "entities": [
        { "type": "PHONE"|"URL"|"EMAIL"|"ORGANIZATION"|"CRYPTO_WALLET", "value": "extracted value", "verificationStatus": "What you found about this specific entity", "isFlagged": boolean }
      ],
      "evidencePoints": ["List of specific reasons for the score"],
      "recommendation": "Actionable advice for the user"
    }
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: mimeType,
              data: base64Image,
            },
          },
          { text: prompt },
        ],
      },
      config: {
        tools: [{ googleSearch: {} }],
        temperature: 0.1, // Low temperature for analytical precision
      },
    });

    console.log(response);

    const text = response.text || '{}';

    // Extract JSON from potential markdown code blocks
    let cleanJson = text;
    const jsonMatch =
      text.match(/```json\n([\s\S]*?)\n```/) || text.match(/```([\s\S]*?)```/);
    if (jsonMatch) {
      cleanJson = jsonMatch[1];
    } else {
      // sometimes it might just be the object
      const firstBrace = text.indexOf('{');
      const lastBrace = text.lastIndexOf('}');
      if (firstBrace !== -1 && lastBrace !== -1) {
        cleanJson = text.substring(firstBrace, lastBrace + 1);
      }
    }

    let parsedData: any;
    try {
      parsedData = JSON.parse(cleanJson);
    } catch (e) {
      console.error('Failed to parse JSON', e, cleanJson);
      throw new Error('Analysis failed to produce structured data.');
    }

    // Extract grounding sources if available
    const sources: Array<{ title: string; uri: string }> = [];
    if (response.candidates?.[0]?.groundingMetadata?.groundingChunks) {
      response.candidates[0].groundingMetadata.groundingChunks.forEach(
        (chunk: any) => {
          if (chunk.web?.uri) {
            sources.push({
              title: chunk.web.title || 'Web Source',
              uri: chunk.web.uri,
            });
          }
        }
      );
    }

    // Map to our TypeScript interface
    const result: VerificationResult = {
      riskScore: parsedData.riskScore || 0,
      verdict: (parsedData.verdict as Verdict) || Verdict.SUSPICIOUS,
      summary: parsedData.summary || 'No summary provided.',
      entities: Array.isArray(parsedData.entities)
        ? parsedData.entities.map((e: any) => ({
            type: (e.type as EntityType) || EntityType.ORGANIZATION,
            value: e.value || 'Unknown',
            verificationStatus: e.verificationStatus || 'Unverified',
            isFlagged: !!e.isFlagged,
          }))
        : [],
      evidencePoints: Array.isArray(parsedData.evidencePoints)
        ? parsedData.evidencePoints
        : [],
      recommendation: parsedData.recommendation || 'Proceed with caution.',
      sources: sources,
    };

    return result;
  } catch (error) {
    console.error('Gemini Analysis Error:', error);
    throw error;
  }
};
