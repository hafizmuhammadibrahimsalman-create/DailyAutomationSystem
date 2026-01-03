
import asyncio
import os
from pathlib import Path
from typing import List, Dict
import edge_tts
from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoGenerator:
    """Generates a daily news briefing video."""
    
    def __init__(self, output_dir: str = "media_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.fonts_dir = Path("fonts") # Placeholder if we had custom fonts
        
    async def create_video_briefing(self, report_data: Dict) -> str:
        """Main pipeline to create the video."""
        print("🎬 Starting Video Generation...")
        
        # 1. Generate Voiceover Script
        full_script = self._create_script(report_data)
        audio_path = self.output_dir / "voiceover.mp3"
        
        # 2. Generate Audio (Async)
        print("Scanning news to audio...")
        communicate = edge_tts.Communicate(full_script, "en-US-AndrewMultilingualNeural")
        await communicate.save(str(audio_path))
        
        # 3. Generate Slides
        print("🎨 Drawing slides...")
        clips = []
        duration_per_slide = 5 # Placeholder, ideally we sync with audio, but for simple MVP we just show a general background or loop
        
        # Create a title slide
        title_img = self._create_slide("Daily News Intelligence", "Your Personal Briefing")
        title_clip = ImageClip(str(title_img)).with_duration(3)
        clips.append(title_clip)
        
        # Create topic slides
        for topic, items in report_data.items():
            if not items: continue
            
            # Topic Header
            slide = self._create_slide(topic.upper(), f"{len(items)} Key Updates")
            clips.append(ImageClip(str(slide)).with_duration(3))
            
            # News Items
            for item in items[:2]: # Show max 2 items per topic in video
                slide = self._create_slide(item['title'][:50]+"...", item['source'])
                clips.append(ImageClip(str(slide)).with_duration(4))
                
        # 4. Assemble Video
        print("🎞️ Rendering final video...")
        
        # Combine visual clips
        final_visual = concatenate_videoclips(clips)
        
        # Load audio
        audio = AudioFileClip(str(audio_path))
        
        # Adjust video length to match audio (simple loop / freeze last frame method)
        if final_visual.duration < audio.duration:
            # simple finish: hold the last frame
            final_visual = final_visual.with_duration(audio.duration)
        else:
            final_visual = final_visual.subclipped(0, audio.duration)
            
        final_video = final_visual.with_audio(audio)
        
        # Write output
        output_path = self.output_dir / "daily_briefing.mp4"
        final_video.write_videofile(
            str(output_path), 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            preset="ultrafast",  # speed over size
            threads=4
        )
        
        return str(output_path)

    def _create_script(self, data: Dict) -> str:
        """Turn structured news data into a readable script."""
        script = ["Welcome to your daily intelligence briefing."]
        
        for topic, items in data.items():
            if not items: continue
            friendly_topic = topic.replace("_", " ").title()
            script.append(f"In {friendly_topic}:")
            for item in items[:2]:
                script.append(item['title'] + ".")
                
        script.append("That's all for today. Stay informed.")
        return " ".join(script)

    def _create_slide(self, title: str, subtitle: str) -> Path:
        """Create a 1080x1920 (Portrait) or 1920x1080 (Landscape) image."""
        width, height = 1280, 720 # Landscape for now
        img = Image.new('RGB', (width, height), color=(15, 23, 42)) # Dark Blue Slate
        draw = ImageDraw.Draw(img)
        
        # Basic centered text (using default font since we don't have custom ones guaranteed)
        # In a real app we'd load a .ttf
        
        try:
            # dynamic font size (limited by default font, but let's try to simulate)
            # Actually default font is too small. We really need a TTF.
            # I'll rely on a system font if possible, or basic
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_sub = ImageFont.truetype("arial.ttf", 40)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            
        # Draw Title
        draw.text((width/2, height/2 - 50), title, font=font_title, fill="white", anchor="mm")
        
        # Draw Subtitle
        draw.text((width/2, height/2 + 50), subtitle, font=font_sub, fill="#94a3b8", anchor="mm")
        
        filename = self.output_dir / f"slide_{hash(title)}.png"
        img.save(filename)
        return filename

# Wrapper for synchronous call
def generate_video(news_data):
    generator = VideoGenerator()
    return asyncio.run(generator.create_video_briefing(news_data))

if __name__ == "__main__":
    # Test
    test_data = {
        "AI": [{"title": "GPT-5 Released", "source": "TechCrunch"}],
        "Pakistan": [{"title": "New Metro Line Opens", "source": "Dawn"}]
    }
    generate_video(test_data)
