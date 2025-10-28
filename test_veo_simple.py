#!/usr/bin/env python3
"""Simple test of Veo API with a startup brief."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "agent_root"))

from forge.agents.video_agent.veo_client import VeoClient
from forge.config import config

logging.basicConfig(level=logging.INFO)

async def test_veo_with_brief():
    """Test Veo with a simple startup pitch."""
    
    # Simple startup pitch prompt
    prompt = """
    A sleek, modern tech startup office. A diverse team collaborates around a holographic display 
    showing AI-powered analytics. The camera smoothly pans across the room, showing engaged professionals 
    pointing at data visualizations. The scene conveys innovation, teamwork, and cutting-edge technology. 
    Cinematic lighting, professional atmosphere, Silicon Valley aesthetic.
    """
    
    try:
        # Initialize VeoClient
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "mock-project")
        veo_client = VeoClient(project_id=project_id, model_name=config.video_model)
        
        print(f"Testing Veo API with project: {project_id}")
        print(f"Model: {config.video_model}")
        print(f"Prompt: {prompt.strip()}")
        print("-" * 80)
        
        # Generate video (Veo will create an 8-second clip)
        video_bytes = await veo_client.generate_video(
            prompt=prompt.strip(),
            duration_seconds=8,  # This is ignored by API but kept for interface compatibility
            aspect_ratio="16:9",  # This is ignored by API but kept for interface compatibility
            style="cinematic"  # This is ignored by API but kept for interface compatibility
        )
        
        # Save the video
        output_path = Path("test_veo_output.mp4")
        output_path.write_bytes(video_bytes)
        
        print(f"✅ Success! Video saved to: {output_path}")
        print(f"   Size: {len(video_bytes):,} bytes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTo use real Veo API, set either:")
        print("  export GOOGLE_API_KEY='your-api-key'")
        print("  or")
        print("  export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("  export GOOGLE_GENAI_USE_VERTEXAI=TRUE")

if __name__ == "__main__":
    asyncio.run(test_veo_with_brief())
