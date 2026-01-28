# Dynamic Role Management System

## Overview
The mobility application now includes a comprehensive role management system that allows Super Admins to create, modify, and delete roles dynamically. This system supports hierarchical role structures that can be adapted to any business process or organizational structure.

## Features

### 1. **Hierarchical Role Structure**
- Roles can have parent-child relationships
- Level-based authority system (0-100)
- Visual role tree display
- Unlimited depth in hierarchy

### 2. **Dynamic Role Creation**
- Create new roles without code changes
- Define custom permissions per role
- Set role levels for authority hierarchy
- Assign parent roles for inheritance

### 3. **Role Permissions**
Built-in permissions include:
- `view_users` - View user information
- `manage_users` - Create, edit, delete users
- `view_departments` - View department structure
- `manage_departments` - Create, edit, delete departments
- `view_questions` - View checklist questions
- `manage_questions` - Create, edit, delete questions
- `view_checklists` - View checklist assignments
- `manage_checklists` - Create, assign, manage checklists

### 4. **System Roles Protection**
- System roles cannot be deleted
- Critical roles (super_admin, admin, operator) are protected
- Prevents accidental deletion of core roles

### 5. **User Assignment Validation**
- Cannot delete roles with active users
- Cannot delete roles with child dependencies
- Audit trail for all role changes

## Accessing Role Management

### For Super Admin:
1. Login with Super Admin credentials
2. Click **"MANAGE ROLES"** button in the navigation bar
3. Access the role management dashboard

## Role Management Interface

### Main Dashboard
- **Role Hierarchy Tree** - Visual representation of role relationships
- **Roles Table** - Detailed list of all roles with:
  - Level indicator
  - Role name (system identifier)
  - Display name (user-friendly name)
  - Parent role
  - Number of users assigned
  - Status (Active/Inactive, System/Custom)
  - Action buttons (View, Edit, Delete)

### Creating a New Role

1. Click **"Create New Role"** button
2. Fill in the form:
   - **Role Name**: System identifier (lowercase, underscores only)
     - Example: `team_leader`, `shift_supervisor`, `quality_inspector`
   - **Display Name**: User-friendly name
     - Example: "Team Leader", "Shift Supervisor", "Quality Inspector"
   - **Description**: Role responsibilities and purpose
   - **Level (0-100)**: Authority level
     - 0-9: Basic users
     - 10-29: Operators and field workers
     - 30-49: Team leaders and supervisors
     - 50-69: Managers and department heads
     - 70-89: Senior managers
     - 90-99: Executives
     - 100: Super Admin (highest authority)
   - **Parent Role**: Select parent to create hierarchy
   - **Permissions**: Check applicable permissions
3. Click **"Create Role"**

### Editing a Role

1. Click the **Edit** button (pencil icon) next to a role
2. Modify any field except the system name
3. Update permissions as needed
4. Click **"Update Role"**

**Note**: System roles have limited editability to maintain system integrity.

### Deleting a Role

1. Click the **Delete** button (trash icon) next to a role
2. Confirm the deletion

**Restrictions**:
- Cannot delete system roles
- Cannot delete roles with assigned users
- Cannot delete roles with child roles
- Must reassign users before deletion

### Viewing Role Details

1. Click the **View** button (eye icon) next to a role
2. See detailed information:
   - Basic details (name, level, parent)
   - Status information
   - Number of users assigned
   - Number of child roles
   - All assigned permissions
   - Creation and update timestamps

## Example Role Hierarchies

### Example 1: Manufacturing Company
```
Super Admin (100)
├── Plant Manager (80)
│   ├── Production Manager (70)
│   │   ├── Shift Supervisor (50)
│   │   │   ├── Team Leader (40)
│   │   │   │   └── Operator (20)
│   │   └── Quality Inspector (45)
│   └── Maintenance Manager (70)
│       └── Maintenance Technician (30)
└── Safety Officer (75)
```

### Example 2: Logistics Company
```
Super Admin (100)
├── Operations Director (90)
│   ├── Warehouse Manager (70)
│   │   ├── Inventory Supervisor (50)
│   │   └── Warehouse Operator (30)
│   └── Transport Manager (70)
│       ├── Dispatcher (50)
│       └── Driver (25)
└── Compliance Manager (80)
```

### Example 3: Service Company
```
Super Admin (100)
├── Service Manager (80)
│   ├── Field Service Manager (70)
│   │   ├── Senior Technician (50)
│   │   └── Technician (35)
│   └── Customer Service Manager (70)
│       ├── Service Coordinator (45)
│       └── Service Representative (30)
└── Quality Manager (75)
```

## API Endpoints

### GET `/superadmin/manage_roles`
View the role management dashboard
- **Access**: Super Admin only
- **Returns**: HTML page with role tree and table

### POST `/create_role`
Create a new role
- **Access**: Super Admin only
- **Parameters**:
  - `name` (string, required): System identifier
  - `display_name` (string, required): User-friendly name
  - `description` (text, optional): Role description
  - `level` (integer, required): Authority level (0-100)
  - `parent_role_id` (integer, optional): Parent role ID
  - `permissions[]` (array, optional): List of permission keys
- **Returns**: Redirect to manage_roles with success/error message

### POST `/update_role/<role_id>`
Update an existing role
- **Access**: Super Admin only
- **Parameters**: Same as create_role
- **Returns**: Redirect to manage_roles with success/error message

### POST `/delete_role/<role_id>`
Delete a role
- **Access**: Super Admin only
- **Returns**: JSON response with success status

### GET `/api/role/<role_id>`
Get detailed role information
- **Access**: Super Admin only
- **Returns**: JSON with complete role details

## Database Schema

### Role Model
```python
class Role(db.Model):
    id = Integer (Primary Key)
    name = String(50) (Unique, System identifier)
    display_name = String(100) (User-friendly name)
    description = Text (Role description)
    permissions = JSONB (Flexible permission storage)
    level = Integer (Authority level 0-100)
    parent_role_id = Integer (Foreign Key to roles.id)
    is_active = Boolean (Active status)
    is_system_role = Boolean (System protection flag)
    created_at = DateTime
    updated_at = DateTime
```

## Best Practices

### 1. **Role Naming**
- Use descriptive, clear names
- System names: lowercase with underscores
- Display names: Title Case for readability

### 2. **Level Assignment**
- Leave gaps between levels for future additions
- Group similar roles in level ranges
- Reserve 100 for Super Admin only

### 3. **Permission Assignment**
- Grant minimum necessary permissions
- Use parent-child relationships for inheritance
- Review permissions regularly

### 4. **Role Hierarchy**
- Keep hierarchy depth reasonable (3-5 levels)
- Align with organizational structure
- Document role relationships

### 5. **Role Maintenance**
- Deactivate unused roles instead of deleting
- Review and update permissions periodically
- Audit role assignments regularly

## Security Considerations

### 1. **Access Control**
- Only Super Admin can manage roles
- Level-based authority checks
- Audit logging for all role changes

### 2. **System Protection**
- System roles cannot be deleted
- Critical permissions preserved
- Cascade checks before deletion

### 3. **User Safety**
- Cannot delete roles with active users
- Cannot delete roles with dependencies
- Requires explicit confirmation for deletion

## Audit Trail

All role management operations are logged:
- **create_role**: New role creation
- **update_role**: Role modifications
- **delete_role**: Role deletion

Each audit entry includes:
- User who performed the action
- Timestamp
- Old values (for updates)
- New values
- Action description

## Troubleshooting

### Cannot Delete Role
**Issue**: "Cannot delete role. X users still assigned to this role"
**Solution**: Reassign users to different roles before deletion

### Cannot Delete Role with Children
**Issue**: "Cannot delete role. X child roles depend on this role"
**Solution**: 
1. Delete child roles first, OR
2. Reassign child roles to different parent, OR
3. Make child roles top-level (no parent)

### Role Not Appearing in Dropdown
**Issue**: New role not showing in user registration
**Solution**: 
1. Ensure role is marked as Active
2. Refresh the registration page
3. Check role creation was successful

### Permission Changes Not Effective
**Issue**: Updated permissions not working for users
**Solution**: Users may need to log out and log back in for permission changes to take effect

## Future Enhancements

Potential improvements for the role management system:

1. **Permission Inheritance**
   - Child roles inherit parent permissions
   - Override specific permissions

2. **Role Templates**
   - Pre-defined role templates for common structures
   - Quick setup for new organizations

3. **Bulk Operations**
   - Batch user assignment
   - Bulk permission updates

4. **Role Analytics**
   - Usage statistics per role
   - Permission utilization reports

5. **Custom Permissions**
   - Define custom permission keys
   - Dynamic permission creation

6. **Role Workflows**
   - Approval process for role creation
   - Change request tracking

## Support

For assistance with role management:
1. Check this documentation
2. Review audit logs for changes
3. Contact system administrator
4. Escalate to Super Admin if needed

## Version History

- **v1.0** (2026-01-28): Initial role management system
  - Create, edit, delete roles
  - Hierarchical structure support
  - Permission management
  - Audit logging
