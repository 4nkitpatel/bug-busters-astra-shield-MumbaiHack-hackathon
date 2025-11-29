import React, { useState, useEffect, useCallback } from 'react';
import { Claim, ClaimSource, Verdict, VerificationResult } from '../types';
import RealTimeFeed from './RealTimeFeed';
import StatsPanel from './StatsPanel';
import ImpactVisualization from './ImpactVisualization';
import { verifyTextClaim } from '../services/geminiService';

interface MonitoringDashboardProps {
  userResult: VerificationResult | null;
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({
  userResult,
}) => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [stats, setStats] = useState({
    monitored: 14205,
    verifying: 0,
    debunked: 843,
  });
  const [chartData, setChartData] = useState<any[]>([]);

  // Initialize chart data
  useEffect(() => {
    const initialData = Array.from({ length: 15 }, (_, i) => ({
      time: i,
      threats: Math.floor(Math.random() * 20) + 5,
      verified: Math.floor(Math.random() * 15) + 10,
    }));
    setChartData(initialData);
  }, []);

  // Fetch Real Trending News via free proxy API
  useEffect(() => {
    const loadRealNews = async () => {
      setStats((prev) => ({ ...prev, verifying: 1 }));
      try {
        const response = await fetch(
          'https://saurav.tech/NewsAPI/top-headlines/category/general/in.json'
        );
        const data = await response.json();

        if (data.articles && data.articles.length > 0) {
          // Take top 8 articles
          const articles = data.articles.slice(0, 8);

          // Process sequentially with delay to simulate live feed
          for (let i = 0; i < articles.length; i++) {
            const item = articles[i];
            const id = Math.random().toString(36).substr(2, 9);

            // 1. Add to feed as VERIFYING
            const initialClaim: Claim = {
              id,
              text: item.title,
              source: item.source.name || 'News API',
              timestamp: 'Just now',
              engagementSpike: 'Trending',
              status: 'VERIFYING', // Initial status
              url: item.url,
            };

            setClaims((prev) => [initialClaim, ...prev].slice(0, 50));

            // 2. Perform Verification in background
            verifyTextClaim(item.title).then((result) => {
              setClaims((currentClaims) =>
                currentClaims.map((c) =>
                  c.id === id
                    ? {
                        ...c,
                        status: 'VERIFIED',
                        verdict: result.verdict,
                        riskScore: result.riskScore,
                      }
                    : c
                )
              );

              // Update stats
              setStats((prev) => ({
                ...prev,
                monitored: prev.monitored + 1,
                debunked:
                  prev.debunked + (result.verdict !== Verdict.SAFE ? 1 : 0),
                verifying: prev.verifying > 0 ? prev.verifying - 0.1 : 0,
              }));
            });

            // Update Chart slightly
            setChartData((prev) => [
              ...prev.slice(1),
              {
                time: Date.now(),
                threats: Math.floor(Math.random() * 25) + 5,
                verified: Math.floor(Math.random() * 20) + 10,
              },
            ]);

            // Delay next item
            await new Promise((r) => setTimeout(r, 2000));
          }
        }
      } catch (e) {
        console.error('Error loading news', e);
      } finally {
        setStats((prev) => ({ ...prev, verifying: 0 }));
      }
    };

    loadRealNews();
  }, []);

  // Handle User Result Injection
  useEffect(() => {
    if (userResult) {
      // Find a summarized text from entities or summary
      let claimText = userResult.summary.substring(0, 100) + '...';
      if (userResult.entities.length > 0) {
        claimText = `Verify: ${userResult.entities[0].value}`;
      }

      const id = Math.random().toString(36).substr(2, 9);
      const newClaim: Claim = {
        id,
        text: claimText,
        source: 'User Upload',
        timestamp: 'Just now',
        engagementSpike: '',
        status: 'VERIFIED',
        verdict: userResult.verdict,
        riskScore: userResult.riskScore,
        isUserSubmission: true,
      };

      setClaims((prev) => [newClaim, ...prev].slice(0, 10));

      // Force update stats
      setStats((prev) => ({
        ...prev,
        monitored: prev.monitored + 1,
        debunked: prev.debunked + (userResult.verdict !== Verdict.SAFE ? 1 : 0),
      }));
    }
  }, [userResult]);

  return (
    <div className="w-full max-w-6xl mx-auto mt-16 pt-10 border-t border-slate-800 animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight flex items-center">
            <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-3"></span>
            Global Verification Stream (India)
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            Real-time trending news analysis powered by Gemini.
          </p>
        </div>
        <div className="hidden md:flex items-center space-x-2 text-xs font-mono text-slate-500 bg-slate-900 px-3 py-1 rounded border border-slate-800">
          <i className="fas fa-server"></i>
          <span>NODE_ID: ASTRA_APAC_04</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
        {/* Left: Feed */}
        <div className="lg:col-span-2 bg-slate-950/50 border border-slate-800 rounded-2xl p-4 shadow-inner">
          <RealTimeFeed claims={claims} />
        </div>

        {/* Right: Stats */}
        <div className="lg:col-span-1">
          <StatsPanel stats={stats} chartData={chartData} />
        </div>
      </div>

      {/* Bottom: Impact */}
      <ImpactVisualization />
    </div>
  );
};

export default MonitoringDashboard;
