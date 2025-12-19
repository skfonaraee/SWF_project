# Study Without Fear 🎓

A comprehensive web application for helping Kazakhstani students find international study programs and scholarships.

## 🌟 Features

- **Authentication System** - Secure registration and login with comprehensive validation
- **Role-Based Access** - Three distinct user roles: Student, Admin, and Moderator
- **Language Support** - Full support for English and Russian
- **Student Dashboard** - Complete personal cabinet with profile, favorites, application tracker, and AI history
- **Admin Panel** - User management, statistics, and platform monitoring
- **Moderator Panel** - Content management for programs and scholarships
- **Telegram Integration** - Bot connection for notifications and reminders
- **Scholarship Directory** - Comprehensive list of scholarships by region
- **Responsive Design** - Works seamlessly on desktop and mobile devices

## 🚀 Quick Start

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## 🔑 Test Credentials

### Admin Account
- **Email**: `admin@studywithoutfear.com`
- **Password**: `Admin@123`

### Moderator Account
- **Email**: `moderator@studywithoutfear.com`
- **Password**: `Moderator@123`

### Student Account
- Create any account via the registration form
- All registered accounts (except admin/moderator) are created as student accounts

## 📱 Features by Role

### Student Role
- **Profile Management**: Avatar, education goal, specialization
- **Telegram Integration**: Connect bot for deadline reminders and scholarship updates
- **Saved Programs**: Bookmark favorite programs
- **Application Tracker**: Track applications with statuses (Watching, Preparing, Applied, Accepted, Rejected)
- **AI Assistant**: Access conversation history
- **Settings**: Language, theme, timezone (fixed to Kazakhstan UTC+5)
- **Security**: Change password, view login history

### Admin Role
- **Statistics Dashboard**: User metrics, application counts, AI usage
- **User Management**: View, add, edit, delete users
- **Program Management**: Full CRUD operations
- **Scholarship Management**: Add and manage scholarships
- **AI Logs**: Monitor assistant usage and queries

### Moderator Role
- **Program Management**: Add, edit, delete programs
- **Scholarship Management**: Add, edit, delete scholarships

## 🌐 Language Switching

Click the language toggle in the top navigation bar to switch between:
- **ENG** - English
- **РУС** - Russian

All UI elements are fully translated.

## 📋 Password Requirements

When registering, your password must meet these criteria:
- 8-20 characters in length
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (@, #, $, !)
- Cannot contain your username or email
- Cannot be a weak password (password, qwerty, 123456, etc.)

## 🔗 Scholarship Links

The platform includes links to official scholarship websites for:
- **Europe**: Erasmus+, Stipendium Hungaricum, DAAD, Chevening, Eiffel
- **United States**: Fulbright, QuestBridge, Gates, Global UGRAD
- **Canada**: Vanier, Lester B. Pearson, Canadian Commonwealth
- **Australia**: Australia Awards, Endeavour Scholarships
- **Asia**: MEXT, Chinese Government Scholarship, KGSP, NUS/NTU
- **Southeast Asia**: ASEAN Scholarships, Monash Malaysia, RMIT Vietnam
- **UAE**: Emirates Scholarship, Dubai Government Scholarships

## 🛠️ Technology Stack

- **React** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **shadcn/ui** - UI components
- **Lucide React** - Icons
- **Sonner** - Toast notifications

## 📖 Documentation

- **IMPLEMENTATION_SUMMARY.md** - Complete feature overview
- **INTEGRATION_GUIDE.md** - Backend integration guide for Django/FastAPI

## 🎯 Target Users

This platform is specifically designed for:
- Kazakhstani students seeking international education opportunities
- Schools and educational institutions in Kazakhstan
- Study abroad advisors and consultants

## ⏰ Timezone

All dates and times are displayed in Kazakhstan timezone (UTC+5).

## 🤝 Contributing

This is a frontend application ready to be integrated with a Django or FastAPI backend. See `INTEGRATION_GUIDE.md` for detailed backend specifications.

## 📞 Support

For questions or issues, please refer to the documentation or contact the development team.

---

**Platform**: Study Without Fear  
**Version**: 1.0.0  
**License**: Proprietary  
**Target Region**: Kazakhstan  
**Languages**: English, Russian
