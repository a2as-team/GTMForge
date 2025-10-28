"""
Website Specification Agent
Creates comprehensive website specification from GTM brief for landing page development.
"""

import logging
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from forge.data_models import Assets, ReportAsset
from forge.utils.callbacks import create_asset_save_callback


website_spec_prompt = """
You are a Website Specification Expert. Analyze the GTM brief and create a comprehensive specification for a professional landing page.

INPUT
You will receive a GTM brief from the 'company_brief' state key.

OUTPUT
Create a detailed website specification in markdown with these sections:

# Website Specification for [Company Name]

## 1. Executive Summary
- Website purpose and goals
- Target audience
- Primary conversion goal

## 2. Brand & Messaging
- Brand voice and tone
- Core value proposition
- Key differentiators

## 3. Page Sections

For each major section (Hero, Features, Product Showcase, Video, Use Cases, Social Proof, Pitch Deck, FAQ, CTA):
- Purpose and content elements
- Copy and messaging
- **For visual sections**: Include detailed Imagen prompts (minimum 80 words) specifying layout, colors, style, mood, and specific elements

### Screenshot Carousel Requirements
Generate 5 product screenshots with:
- Descriptive title
- What it shows
- Key UI elements
- **Imagen Generation Prompt** (minimum 80 words): Ultra-detailed UI mockup description including layout, color scheme, specific text on buttons/labels, visual style, and branding

### Promo Video Section
- 15-second video script with scene-by-scene breakdown
- **Veo Generation Prompt** (minimum 100 words): Comprehensive video prompt with visual style, scenes, pacing, transitions, text overlays, and mood

## 4. Design Guidelines
- Color palette direction (moods, not hex codes)
- Typography style (font families suggestions)
- Visual aesthetic
- Imagery style

## 5. Technical Requirements

### Architecture
- **Single HTML file** with embedded CSS and JavaScript
- No external dependencies except asset server media
- No frameworks (pure vanilla HTML/CSS/JS)
- Chrome browser target

### CSS
- BEM naming convention (Block__Element--Modifier)
- CSS Custom Properties for theming
- CSS Grid and Flexbox for layout
- Mobile-first responsive design
- Moderate animations and transitions

### JavaScript
- Vanilla ES6+ JavaScript
- Required features: carousel, smooth scrolling, mobile menu, scroll animations
- Intersection Observer API for performance

### Responsive Design
- Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- Touch-friendly (minimum 44x44px tap targets)

### Accessibility
- WCAG 2.1 Level AA compliance
- Semantic HTML5 elements
- Proper alt text and ARIA labels
- Keyboard navigation support

### Asset References
Use this format for asset paths:
- Images: `/assets/[session_id]/images/[filename]`
- Videos: `/assets/[session_id]/videos/[filename]`
- PDFs: `/assets/[session_id]/decks/[filename]`

---

IMPORTANT:
- Extract content intelligently from the company_brief state
- All Imagen prompts minimum 80 words, Veo prompts minimum 100 words
- Be specific with visual descriptions
- Maintain cohesive brand voice throughout
"""


# Generate callback using factory to reduce boilerplate
save_website_spec_callback = create_asset_save_callback(
    state_key="website_spec",
    asset_type="website_specs",
    filename="website_specification.md",
)


# ADK agent definition
website_spec_agent = Agent(
    name="website_spec_agent",
    description="Creates comprehensive website specification from GTM brief, including detailed asset generation requirements for images, video, and pitch deck",
    instruction=website_spec_prompt,
    output_key="website_spec",
    after_agent_callback=save_website_spec_callback,
)
