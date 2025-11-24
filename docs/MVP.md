# 🚀 Minimum Viable Product (MVP)
## **Qwik – Real-Time Micro-Moment Social Media Website**

The MVP defines the minimum set of features required for Qwik to function as a usable, testable, and demonstrable product. These features ensure users can create micro-moment posts (Qwips), interact socially, and experience the core concept of authenticity and real-time sharing.

---

# 1. MVP Goals

- Deliver a functional core social media experience.
- Validate the concept of temporary micro-posts (Qwips).
- Ensure smooth user onboarding and interaction.
- Provide a basic but stable communication and notification system.
- Enable admin moderation to maintain platform safety.

---

# 2. MVP Functional Requirements

Below are the **essential features** included in the MVP.

---

## 2.1 User Authentication (Essential)
- Register with email, username, password  
- Login / Logout  
- Basic profile update (name, bio, profile picture)  
- Password encryption (secure hashing)

---

## 2.2 Qwips (Core Feature)
- Create a Qwip (image/video/text)  
- Add caption  
- Choose temporary (24 hr) or permanent  
- Temporary posts automatically disappear  
- View own posts and others' posts  
- Simple home feed (most recent posts)

---

## 2.3 Interactions
### Likes
- Like/unlike posts  
- Display like count  

### Comments
- Add comment  
- View comments under posts  

### Follow System
- Follow/unfollow users  
- View follower/following count  

---

## 2.4 Explore Page
- View public Qwips from all users  
- Simple sorting: latest first  

---

## 2.5 Messaging (MVP Version)
- One-to-one messaging  
- Text messages only (no media in MVP)  
- Mark message as read  

---

## 2.6 Notifications
Trigger notifications for:
- Likes  
- Comments  
- Follows  
- Messages  

Notification list:
- Show list of notifications  
- Mark as read/unread  

---

## 2.7 Reporting (Basic Moderation)
- User can report:
  - A post  
  - A user  

- Store report in database  

---

## 2.8 Admin Panel (MVP Version)
- View reports  
- Review report details  
- Mark report as:
  - pending  
  - reviewed  
  - action_taken  
- Delete/disable abusive posts  
- Block abusive users  

---

# 3. Features Not Included in MVP (Future)
These will be added after validation of the MVP.

### Future Enhancements
- Micro-challenges  
- Group chat  
- Feed algorithm (trending, recommended)  
- Post insights  
- Stories/filters  
- Video compression  
- Push notifications  
- Activity log analytics  
- Advanced profile customization  

---

# 4. MVP Architecture

### Frontend
- HTML  
- CSS  
- JavaScript (AJAX for dynamic loading)

### Backend
- Django  
- Basic Django templates + views or Django REST API

### Database
- PostgreSQL  
- 10 primary tables (users, posts, likes, comments, follows, messages, notifications, reports, feedback, activity_log)

### Storage
- Local media folder (for MVP)  
- Optional switch to Firebase/S3 later  

---

# 5. MVP User Flow

### New User Flow
1. Sign up → Login  
2. Set profile picture + bio  
3. View feed  
4. Create first Qwip  
5. Like/comment on others' Qwips  
6. Follow users  
7. Receive first notifications  

### Admin Flow
1. Login as admin  
2. View all reports  
3. Open report details  
4. Mark reviewed and take action  
5. Block user or remove content  

---

# 6. MVP Success Criteria

### Product Validation
- Users are able to create and interact with Qwips easily  
- Temporary posts auto-expire correctly  
- Basic messaging works reliably  
- Admin moderation functions smoothly  
- No major usability issues  
- Platform remains stable with up to 500 users  

### Technical Validation
- Database structure supports core social interactions  
- Backend handles essential CRUD operations  
- Frontend loads quickly (<2s feed load time)  
- Secure login and data protection  

---

# 7. MVP Deliverables

- Full stack working website  
- Core features:
  - Authentication  
  - Qwips  
  - Likes/comments  
  - Follows  
  - Messaging  
  - Notifications  
  - Admin moderation  
- Database schema + migrations  
- PRD.md  
- MVP.md  
- API documentation (if REST is used)  
- User manual (optional)  

---

# 8. Conclusion

This MVP allows Qwik to function as a minimal but fully usable micro-moment social media platform. It captures the essence of the final product—quick, real, and authentic sharing—while providing essential social interactions and moderation capabilities. After MVP launch, the product can be expanded with richer features like challenges, analytics, and visual enhancements.

