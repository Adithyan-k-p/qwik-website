# 📄 Product Requirements Document (PRD)
## **Qwik – Real-Time Micro-Moment Social Media Website**

---

## 1. Overview

### 1.1 Product Name
**Qwik**

### 1.2 Tagline
*A real-time micro-moment social media platform for sharing quick, authentic experiences.*

### 1.3 Product Description
Qwik is a web-based social media platform where users share spontaneous micro-moments called **Qwips**. These short-lived posts allow users to capture real-time experiences with minimal editing. Qwips can be temporary (24 hours) or permanently saved, promoting authenticity and reducing the pressure of curated content.

The system supports:
- **Users:** Create, interact, and communicate.
- **Admins:** Monitor, moderate, and maintain the platform.

---

## 2. Problem Statement
Traditional social networks often showcase polished, edited, and curated content, leading to unrealistic expectations and reduced authenticity. Users need a platform that celebrates real, raw, unfiltered daily moments.

**Qwik** solves this by introducing instant micro-moment posting, community challenges, and auto-expiring content.

---

## 3. Objectives

- Support real-time, spontaneous content sharing.
- Encourage authenticity through temporary posts.
- Provide a complete social experience (likes, comments, follows).
- Deliver a fast, responsive user interface using HTML, CSS, and JavaScript.
- Ensure security and moderation through admin tools.
- Implement scalable backend architecture via Django and PostgreSQL.

---

## 4. Scope

### 4.1 In-Scope
- User authentication & profiles  
- Creating & viewing Qwips  
- Temporary (24 hr) & permanent posts  
- Likes, comments, follows  
- Notifications  
- Messaging  
- Explore page  
- Admin moderation  
- Reporting system  
- Feedback system  

### 4.2 Out of Scope (for this version)
- Face filters / AR effects  
- Video editing tools  
- Group chats  
- Marketplace features  
- Advanced recommendation engine  

---

## 5. User Roles

### 5.1 User
- Register, login, logout  
- Create image/video/text Qwips  
- Choose temporary/permanent posts  
- Like, comment, follow  
- Send messages  
- View notifications  
- Participate in challenges  
- Report posts/users  
- Update profile  

### 5.2 Admin
- Review reports  
- Block/unblock users  
- Delete inappropriate posts  
- Manage challenges  
- View user feedback  
- Track actions via activity logs  

---

## 6. Key Features & Requirements

---

### 6.1 Authentication
**Functional Requirements**
- User registration via email  
- Login and logout  
- Forgot password  
- Profile updates  
- Prevent duplicate emails/usernames  

**Non-Functional**
- Secure password hashing  
- Validation and sanitization  
- Rate limiting  

---

### 6.2 Qwips (Posts)
**Functional Requirements**
- Create text/image/video posts  
- Temporary posts auto-expire after 24 hours  
- Convert temporary → permanent  
- Edit or delete own posts  
- View feed, explore, and trending Qwips  

**Non-Functional**
- Fast uploads  
- Optimized media handling  

---

### 6.3 Social Interaction
#### Likes
- Like/unlike posts  
- Store timestamps  

#### Comments
- Add/view/delete own comments  

#### Follow System
- Follow/unfollow users  
- Prevent self-follow  

---

### 6.4 Explore & Feed
- Chronological and trending Qwips  
- Public profiles  
- Discover challenges  

---

### 6.5 Challenges
- Admin creates challenge prompts  
- Users post Qwips under challenge  
- Filter posts by challenge type  

---

### 6.6 Messaging
- One-to-one private messages  
- Text + media  
- Read receipts  
- Recent chat list  

---

### 6.7 Notifications
Triggers:
- Likes  
- Comments  
- Follows  
- Messages  
- System/Admin alerts  

Users can:
- View notification feed  
- Mark as read/unread  

---

### 6.8 Reporting & Moderation
Users can report:
- Posts  
- Users  

Admins can:
- Review reports  
- Update status (pending → reviewed → action_taken)  
- Add admin notes  

---

### 6.9 Feedback
- Users can submit suggestions  
- Admin reviews and marks status  

---

### 6.10 Activity Log
Stores admin actions:
- Deleted posts  
- Banned users  
- Resolved reports  
- Feedback updates  

---

## 7. Database Design (Table Summary)

| Category | Tables | Description |
|---------|--------|-------------|
| Core | users, posts | User accounts and content |
| Interaction | likes, comments, follows | Engagement |
| Communication | messages | Direct chat |
| System | notifications | Alerts |
| Admin | reports, feedback, activity_log | Moderation tools |
| **Total Tables** | **10** | Complete schema |

(A full table-format structure has been provided earlier.)

---

## 8. System Architecture

### Frontend
- **HTML, CSS, JavaScript**
- Responsive layout
- AJAX for dynamic updates

### Backend
- **Django**
- Django ORM for DB operations
- Django views + templates or REST API

### Database
- **PostgreSQL**

### Storage
- Cloud storage / Django Media folder for media files

### Notifications
- Django signals  
- Polling or WebSockets (optional)

---

## 9. UI/UX Requirements

### General Guidelines
- Minimalistic and clean interface  
- Mobile-responsive layout  
- Attractive and modern color theme  

### Required Screens
- Login / Register  
- Home Feed  
- Create Qwip  
- Explore  
- Notifications  
- Chat  
- Profile  
- Report submission  
- Admin dashboard  

---

## 10. Performance Requirements
- Feed loads within < 2 seconds  
- Media uploads < 5 seconds  
- Notification fetch < 1 second  
- Optimized database indexing  

---

## 11. Security Requirements
- Hash passwords securely (Argon2/Bcrypt)  
- CSRF protection  
- Input sanitization  
- Role-based access control  
- Prevent SQL injection (Django ORM)  
- Rate limiting for actions  

---

## 12. Future Improvements
- AI-driven recommended feed  
- Group chats  
- Story filters/effects  
- Post analytics  
- Save posts privately  

---

## 13. Conclusion
Qwik is a next-generation micro-moment social media platform focused on authenticity and real-time engagement. Built using HTML, CSS, JavaScript, Django, and PostgreSQL, it provides a complete full-stack solution with strong social features, moderation tools, messaging, and a clean user experience. This PRD establishes the foundation for development and academic presentation.

