# Preview Images for Social Media

This folder contains preview images for social media sharing (Open Graph and Twitter Cards).

## Quick Setup

### Option 1: Use the Template (Recommended)

1. Open `preview-template.html` in your browser
2. Take a screenshot at 1200x630px resolution
3. Save as `og-image.png` and `twitter-image.png`

### Option 2: Use Online Tools

**Recommended Tools:**
- [Canva](https://www.canva.com/) - Free, easy to use
- [Figma](https://www.figma.com/) - Professional design tool
- [Placid](https://placid.app/) - Automated social media images

### Option 3: Screenshot Tool (Mac)

1. Open `preview-template.html` in Chrome
2. Press `Cmd + Shift + 5`
3. Select "Capture Selected Window"
4. Take screenshot
5. Resize to 1200x630px if needed

### Option 4: Use Browser DevTools

1. Open `preview-template.html` in Chrome
2. Press `F12` to open DevTools
3. Press `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows)
4. Type "screenshot" and select "Capture full size screenshot"
5. Image will download automatically

## Image Specifications

### Open Graph (Facebook, LinkedIn)
- **Filename:** `og-image.png`
- **Size:** 1200 x 630 pixels
- **Format:** PNG or JPG
- **Aspect Ratio:** 1.91:1

### Twitter Card
- **Filename:** `twitter-image.png`
- **Size:** 1200 x 630 pixels (summary_large_image)
- **Format:** PNG or JPG
- **Aspect Ratio:** 1.91:1

## Design Guidelines

### Current Design:
- ✅ Gradient background (purple to blue)
- ✅ Large airplane emoji icon
- ✅ Clear, bold title
- ✅ Feature highlights
- ✅ Zora Digital branding
- ✅ "AI Agent Showcase" badge

### Best Practices:
- Use high contrast text
- Keep important content in the center
- Avoid text near edges (may be cropped)
- Test on both light and dark backgrounds
- Ensure text is readable at small sizes

## Testing Your Images

### Preview Tools:
- **Facebook:** [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- **Twitter:** [Twitter Card Validator](https://cards-dev.twitter.com/validator)
- **LinkedIn:** Share a test post and check preview

### Local Testing:
1. Update the image paths in `app.py` if using local files
2. Deploy to Streamlit Cloud
3. Share the URL on social media to test

## Current Status

- ✅ Template HTML created
- ⏳ Need to generate actual PNG images
- ⏳ Need to add images to repo

## Next Steps

1. Generate `og-image.png` using one of the methods above
2. Copy to create `twitter-image.png` (or create separate design)
3. Commit images to repo
4. Images will automatically be used for social sharing!

## Notes

- Images are referenced in `app.py` meta tags
- GitHub will serve images via raw.githubusercontent.com
- Images should be optimized (compressed) for faster loading
- Consider creating multiple versions for different campaigns


