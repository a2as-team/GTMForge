"""Video stitching utilities using MoviePy."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
    from moviepy.video.fx import fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logging.warning("MoviePy not available. Video stitching will use fallback method.")


class VideoStitcher:
    """Handles stitching multiple video clips into a single video."""
    
    def __init__(self, transition_duration: float = 0.5):
        """Initialize video stitcher.
        
        Args:
            transition_duration: Duration of fade transitions between clips in seconds
        """
        self.transition_duration = transition_duration
        
        if not MOVIEPY_AVAILABLE:
            logging.warning(
                "MoviePy not installed. Install with: pip install moviepy"
            )
    
    def stitch_clips(
        self,
        clip_paths: List[str],
        output_path: str,
        title_text: Optional[str] = None,
        add_transitions: bool = True
    ) -> Tuple[str, float]:
        """Stitch multiple video clips into a single video.
        
        Args:
            clip_paths: List of paths to video clips to stitch
            output_path: Path where the final video should be saved
            title_text: Optional title text to add at the beginning
            add_transitions: Whether to add fade transitions between clips
            
        Returns:
            Tuple of (output_path, total_duration_seconds)
            
        Raises:
            Exception: If stitching fails
        """
        # Check if MoviePy is available dynamically
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
            from moviepy.video.fx import fadein, fadeout
        except ImportError:
            return self._fallback_stitch(clip_paths, output_path)
        
        clips = []
        
        try:
            # Load all clips
            for i, clip_path in enumerate(clip_paths):
                logging.info(f"Loading clip {i+1}/{len(clip_paths)}: {clip_path}")
                
                clip = VideoFileClip(clip_path)
                
                # Add transitions if requested
                if add_transitions:
                    if i > 0:  # Fade in for all clips except first
                        clip = fadein(clip, self.transition_duration)
                    if i < len(clip_paths) - 1:  # Fade out for all except last
                        clip = fadeout(clip, self.transition_duration)
                
                clips.append(clip)
            
            # Add title card if provided
            if title_text and clips:
                title_clip = self._create_title_card(
                    title_text,
                    duration=3.0,
                    size=clips[0].size
                )
                clips.insert(0, title_clip)
            
            # Concatenate all clips
            logging.info("Concatenating clips...")
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Write the final video
            logging.info(f"Writing final video to {output_path}")
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=tempfile.mktemp(suffix=".m4a"),
                remove_temp=True
            )
            
            total_duration = final_clip.duration
            
            # Clean up resources
            logging.info("Cleaning up resources...")
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logging.info(
                f"Successfully created video: {output_path} "
                f"(duration: {total_duration:.1f}s)"
            )
            
            return output_path, total_duration
            
        except Exception as e:
            # Ensure cleanup even if error occurs
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass
            
            logging.error(f"Failed to stitch videos: {e}")
            raise Exception(f"Video stitching failed: {e}")
    
    def _create_title_card(
        self,
        text: str,
        duration: float,
        size: Tuple[int, int]
    ) -> 'VideoFileClip':
        """Create a title card clip.
        
        Args:
            text: Title text
            duration: Duration of title card in seconds
            size: Size (width, height) of the video
            
        Returns:
            Title card video clip
        """
        # Create text clip
        txt_clip = TextClip(
            text,
            fontsize=min(size[0] // 15, 70),
            color='white',
            font='Arial',
            size=size,
            method='caption'
        ).set_duration(duration)
        
        # Center the text
        txt_clip = txt_clip.set_position('center')
        
        # Add fade in/out
        txt_clip = fadein(txt_clip, 0.5)
        txt_clip = fadeout(txt_clip, 0.5)
        
        # Create black background
        from moviepy.editor import ColorClip
        bg_clip = ColorClip(size=size, color=(0, 0, 0)).set_duration(duration)
        
        # Composite text over background
        title_card = CompositeVideoClip([bg_clip, txt_clip])
        
        return title_card
    
    def _fallback_stitch(
        self,
        clip_paths: List[str],
        output_path: str
    ) -> Tuple[str, float]:
        """Fallback stitching method when MoviePy is not available.
        
        This would typically use ffmpeg directly or another method.
        For now, it just copies the first clip as the output.
        
        Args:
            clip_paths: List of video clip paths
            output_path: Output path
            
        Returns:
            Tuple of (output_path, estimated_duration)
        """
        logging.warning(
            "Using fallback stitch method. Install MoviePy for full functionality."
        )
        
        if not clip_paths:
            raise ValueError("No clips provided for stitching")
        
        # Simple fallback: copy first clip to output
        # In production, this would use subprocess to call ffmpeg
        import shutil
        shutil.copy(clip_paths[0], output_path)
        
        # Estimate duration (would need actual video parsing)
        estimated_duration = len(clip_paths) * 10.0  # Assume 10s per clip
        
        return output_path, estimated_duration
    
    def add_audio_track(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        audio_volume: float = 0.7
    ) -> str:
        """Add background audio track to a video.
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path for output video
            audio_volume: Volume level for audio (0.0 to 1.0)
            
        Returns:
            Path to output video
        """
        if not MOVIEPY_AVAILABLE:
            logging.warning("Cannot add audio without MoviePy")
            return video_path
        
        try:
            from moviepy.editor import AudioFileClip
            
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Adjust audio duration to match video
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            else:
                # Loop audio if it's shorter than video
                audio = audio.loop(duration=video.duration)
            
            # Adjust volume
            audio = audio.volumex(audio_volume)
            
            # Set audio
            final_video = video.set_audio(audio)
            
            # Write output
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac"
            )
            
            # Cleanup
            video.close()
            audio.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            logging.error(f"Failed to add audio: {e}")
            return video_path

