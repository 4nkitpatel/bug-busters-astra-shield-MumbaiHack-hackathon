"""
Example usage of the Disaster Relief Verification System.

This script demonstrates how to use the system programmatically.
"""
import asyncio
from pathlib import Path
from src.forensic_agent import ForensicAgent


async def example_verification():
    """Example of verifying a help flyer."""
    
    # Initialize the forensic agent
    agent = ForensicAgent()
    
    # Path to your test image
    # Replace with actual image path
    image_path = "test_image.jpg"
    
    if not Path(image_path).exists():
        print(f"⚠️  Image not found: {image_path}")
        print("Please provide a valid image path or create a test image.")
        return
    
    print("🔍 Starting forensic investigation...")
    print(f"📸 Analyzing image: {image_path}\n")
    
    # Perform investigation
    result = await agent.investigate(image_path)
    
    # Display results
    print("\n" + "="*70)
    print("📋 INVESTIGATION REPORT")
    print("="*70)
    
    print(f"\n🆔 Case ID: {result.get('case_id')}")
    print(f"⏱️  Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
    print(f"📊 Status: {result.get('status', 'unknown')}")
    
    if result.get('verdict'):
        verdict_emoji = {
            'safe': '✅',
            'suspicious': '⚠️',
            'scam': '❌'
        }
        emoji = verdict_emoji.get(result.get('verdict'), '❓')
        print(f"\n{emoji} VERDICT: {result.get('verdict').upper()}")
        print(f"📈 Risk Score: {result.get('risk_score')}/100")
    
    if result.get('summary'):
        print(f"\n📝 Summary:")
        print("-" * 70)
        print(result.get('summary'))
    
    if result.get('recommendations'):
        print(f"\n💡 Recommendations:")
        print("-" * 70)
        for i, rec in enumerate(result.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
    
    # Show evidence count
    evidence_count = len(result.get('evidence', []))
    if evidence_count > 0:
        print(f"\n🔬 Evidence Collected: {evidence_count} pieces")
        print(f"📁 Case File: {result.get('case_id')}")
    
    print("\n" + "="*70)


async def example_api_usage():
    """Example of using the API programmatically."""
    import httpx
    
    # This would be used when the API server is running
    async with httpx.AsyncClient() as client:
        # Note: This is a placeholder - you'd need an actual image file
        print("📡 API Usage Example:")
        print("""
        import httpx
        
        async with httpx.AsyncClient() as client:
            with open('help_flyer.jpg', 'rb') as f:
                files = {'file': f}
                response = await client.post(
                    'http://localhost:8000/verify',
                    files=files
                )
                result = response.json()
                print(f"Verdict: {result['verdict']}")
        """)


if __name__ == "__main__":
    print("🚨 Disaster Relief Verification System - Example Usage")
    print("="*70)
    print()
    
    # Run example verification
    asyncio.run(example_verification())
    
    # Show API usage example
    print("\n")
    asyncio.run(example_api_usage())

