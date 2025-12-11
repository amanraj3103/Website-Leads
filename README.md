# Dream Axis Travel Solutions - Lead Collection Website

A standalone, beautiful, high-end lead collection webpage for Dream Axis Travel Solutions that matches the design and style of the main website. This is an independent project for collecting lead data through a web form.

## Features

- 🎨 **Modern Design**: Matches the main Dream Axis website with gradient backgrounds, animations, and professional styling
- 📱 **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- ✨ **Smooth Animations**: High-end animations and transitions for a premium user experience
- 📋 **Dynamic Form**: Service-specific fields that appear based on selected service type
- ✅ **Form Validation**: Real-time validation with helpful error messages
- 🔒 **Secure Submission**: Backend API to securely save lead data

## Lead Data Collected

The form collects the following information:

### Service Types:
1. **Education India** - Study in India
   - Desired place of study (Bangalore, Mangalore, Kerala, Others)
   - Course (Nursing, Engineering, MBBS, Others)

2. **Education Abroad** - Study overseas
   - Preferred country (UK, EUROPE, AUSTRALIA, CANADA, USA)

3. **Job Europe** - Work opportunities in Europe
   - Job type (Truck Driver, Welder)

### Personal Information:
- Full Name
- Phone Number
- Email Address
- Place of Residence

## Setup Instructions

### Quick Start (Recommended)

**On macOS/Linux:**
```bash
cd Website_assistant
./start.sh
```

**On Windows:**
```bash
cd Website_assistant
start.bat
```

### Manual Setup

### 1. Install Dependencies

```bash
cd Website_assistant
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python server.py
```

The server will start on `http://localhost:5000`

### 3. Access the Website

Open your browser and navigate to:
```
http://localhost:5000
```

The startup scripts will automatically:
- Create a virtual environment (if it doesn't exist)
- Install all required dependencies
- Start the Flask server

## File Structure

```
Website_assistant/
├── index.html          # Main HTML page
├── styles.css          # Styling matching Dream Axis design
├── script.js           # Form handling and validation
├── server.py           # Flask backend server
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Backend API

### Endpoints

- `POST /api/submit-lead` - Submit lead form data
- `GET /api/health` - Health check endpoint
- `GET /` - Serve the index page

### Lead Data Format

```json
{
  "service": "Education India",
  "education_place": "Bangalore",
  "course": "Nursing",
  "name": "John Doe",
  "phone": "+91 98765 43210",
  "email": "john.doe@email.com",
  "place": "Mumbai, Maharashtra"
}
```

## Data Storage

Lead data is saved to `daily_leads.json` in the Website_assistant directory, following the same format as the Telegram bot. The data is organized by date:

```json
{
  "dd_mm_yyyy": [
    {
      "service": "...",
      "name": "...",
      "phone": "...",
      "email": "...",
      "place": "...",
      "timestamp": "HH:MM:SS"
    }
  ]
}
```

## Customization

### Colors
The color scheme matches the main Dream Axis website:
- Primary Navy: `#1e3a8a`
- Primary Teal: `#0f766e`
- Accent Blue: `#3b82f6`

You can modify colors in `styles.css` by updating the CSS variables in the `:root` section.

### Logo
The logo path is set to `../dream-axis/public/images/dream_axis_logo_new.png`. Update the path in `index.html` if your logo is in a different location.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Notes

- The form includes client-side and server-side validation
- All form submissions are logged with timestamps
- The backend server includes CORS support for cross-origin requests
- Error handling is implemented for both frontend and backend

## Troubleshooting

### Server won't start
- Make sure port 5000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Form submission fails
- Check browser console for errors
- Verify the backend server is running
- Check that `daily_leads.json` is writable

### Logo not displaying
- Verify the logo path is correct
- Ensure the logo file exists at the specified path

## License

This project is part of the Dream Axis Travel Solutions system.
