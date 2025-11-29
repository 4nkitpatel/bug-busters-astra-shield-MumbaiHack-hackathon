"""Main entry point for command-line usage."""
import asyncio
import sys
from pathlib import Path

from src.forensic_agent import ForensicAgent


async def main():
    """Main function for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
        print("\nExample:")
        print("  python main.py examples/help_flyer.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Disaster Relief Verification System")
    print("Forensic Analysis Agent")
    print("=" * 60)
    print(f"\nInvestigating: {image_path}\n")
    
    agent = ForensicAgent()
    
    try:
        result = await agent.investigate(image_path)
        
        print("\n" + "=" * 60)
        print("INVESTIGATION COMPLETE")
        print("=" * 60)
        print(f"\nCase ID: {result.get('case_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
        
        if result.get('verdict'):
            print(f"\nVERDICT: {result.get('verdict').upper()}")
            print(f"Risk Score: {result.get('risk_score')}/100")
        
        if result.get('summary'):
            print(f"\nSummary:")
            print(result.get('summary'))
        
        if result.get('recommendations'):
            print(f"\nRecommendations:")
            for i, rec in enumerate(result.get('recommendations', []), 1):
                print(f"  {i}. {rec}")
        
        if result.get('case_file'):
            print(f"\nCase file saved to: {result.get('case_file')}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\nError during investigation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

