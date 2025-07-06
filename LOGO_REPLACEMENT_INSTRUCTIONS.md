# Logo Replacement Instructions

## Files to Replace

Replace the following placeholder files in `app/static/` with your actual PNG logo files:

### 1. My FirstCare Logos
- **LOGO_MFC_EN.png** - English version logo (recommended size: 180x40px)
- **LOGO_MFC_TH.png** - Thai version logo (recommended size: 180x40px)

### 2. Company Logo
- **AMY_LOGO.png** - A Medical For You company logo (recommended size: 60x60px)

## File Specifications

- **Format**: PNG with transparent background recommended
- **Quality**: High resolution for crisp display
- **Size**: Keep file sizes reasonable for web loading

## Current Usage

- **LOGO_MFC_EN.png**: Used in header top panel (English) and login page
- **LOGO_MFC_TH.png**: Used in header top panel when language is set to Thai
- **AMY_LOGO.png**: Used in footer and login page for company branding

## To Replace Files

1. Stop the Docker container: `docker-compose down`
2. Replace the placeholder files in `app/static/` with your actual PNG files
3. Keep the same filenames
4. Restart the container: `docker-compose up -d`

The logos will automatically appear in:
- Login page header
- Dashboard top panel (language-specific)
- Footer copyright section
