# Edit Feature Implementation Guide

## Overview
This guide explains the edit feature that allows users to manage the database through a login popup. Once authenticated, users can delete users or add new users to the system.

## Features Implemented

### 1. Edit Button
- Located in the top-right corner of the placement page, next to the date range selector
- Opens a login modal when clicked

### 2. Login Modal
- Username and password fields
- Admin credentials (default):
  - Username: `admin`
  - Password: `admin123`
- Error messages displayed if login fails
- Modal remains open after login to access edit functions

### 3. Edit Mode (After Login)
After successful login, the modal shows two main sections:

#### A. Add New User
- Button to toggle the add user form
- Form fields:
  - Name
  - Badge No
  - Card No
  - Department
- Successfully added users show a success message
- Modal stays open for additional operations

#### B. Delete User
- Two sections for deletion:
  - Delete from "Results" table
  - Delete from "No Records" table
- Confirmation dialog appears before deletion
- Sets the `active` column to 0 in the database
- Success/error messages displayed
- Modal stays open for additional operations

### 4. Modal Behavior
- **Does NOT close** after edit/delete/add operations
- Only closes when user manually clicks the ✕ button in the top-right
- Page refreshes automatically when modal is closed if any changes were made

## File Modifications

### 1. `web_script.py` (Flask Routes)
Added:
- Admin credentials configuration
- `/api/login` - Verifies user credentials
- `/api/delete-user` - Sets user's active status to 0
- `/api/add-user` - Adds new user to database

### 2. `db_queries.py` (Database Functions)
Added:
- `delete_user(name)` - Updates user's active status to 0
- `add_user(name, badge_no, card_no, department)` - Inserts new user record

### 3. `templates/placement.html`
Added:
- Edit button in the title section
- Login modal HTML
- Edit mode interface with add/delete forms
- JavaScript functions for:
  - Modal open/close
  - Login submission
  - Add user functionality
  - Delete user confirmation and execution
  - Page refresh on modal close

### 4. `static/css/main.css`
Added:
- Modal styling
- Edit button styling
- Form input styling
- Table styling for edit mode
- Delete button styling
- Responsive design for smaller screens

## Using the Edit Feature

### Step 1: Click Edit Button
Click the "Edit" button in the top-right corner of the placement page.

### Step 2: Login
Enter admin credentials:
- Username: `admin`
- Password: `admin123`

If credentials are incorrect, an error message will appear.

### Step 3: Choose Action

#### To Add a User:
1. Click "Add New User" button
2. Fill in the form:
   - Name
   - Badge No
   - Card No
   - Department
3. Click "Add User"
4. Success message appears
5. Form clears for next entry

#### To Delete a User:
1. Find the user in either Results or No Records table
2. Click the "Delete" button
3. Confirm deletion in the popup
4. Success message appears

### Step 4: Close Modal
Click the ✕ button in the top-right corner of the modal.
Page will automatically refresh if any changes were made.

## Database Schema Requirements

Ensure your `zhaji.cards` table has the following columns:
- `name` (VARCHAR)
- `badge_number` (VARCHAR)
- `card_number` (VARCHAR)
- `department` (VARCHAR)
- `active` (INT, where 1 = active, 0 = inactive)

## Customization

### Change Admin Credentials
Edit `web_script.py`:
```python
ADMIN_USERNAME = "your_username"
ADMIN_PASSWORD = "your_password"
```

### Modify Modal Appearance
Edit `static/css/main.css` for:
- `.modal-content` - Modal box styling
- `.modal-close` - Close button styling
- `.edit-button` - Edit button styling

### Add More Fields
To add fields to the add user form:
1. Add input field in `placement.html`
2. Update `submitAddUser()` function to read new field
3. Update `/api/add-user` route in `web_script.py`
4. Update `add_user()` function in `db_queries.py`

## Error Handling
- Invalid login credentials show error message
- Database errors are caught and displayed
- Form validation ensures all required fields are filled
- Confirmation dialogs prevent accidental deletions

## Security Considerations
- Login credentials are sent via HTTPS in production
- Consider implementing proper session management
- Store passwords securely (bcrypt/hashing) in production
- Implement rate limiting for login attempts
- Add logging for audit trail

## Troubleshooting

### Modal doesn't appear
- Check browser console for JavaScript errors
- Verify Flask server is running
- Clear browser cache

### Login doesn't work
- Verify credentials match those in `web_script.py`
- Check browser console for network errors
- Ensure Flask server is responding

### Database operations fail
- Verify database credentials in `db_queries.py`
- Confirm table schema matches requirements
- Check database connection status
- Review server logs for error messages

### Page doesn't refresh after closing modal
- Ensure modal is closed via the ✕ button
- Check browser console for JavaScript errors
- Verify changes were actually made to database
