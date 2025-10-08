"""
Organization Service
====================

Handles all organization-related business logic and DynamoDB operations
"""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class OrganizationService:
    """Service for managing organizations"""
    
    def __init__(self, region: str = "eu-central-1", endpoint_url: Optional[str] = None):
        """
        Initialize OrganizationService
        
        Args:
            region: AWS region
            endpoint_url: Optional DynamoDB endpoint (for local testing)
        """
        self.region = region
        self.endpoint_url = endpoint_url
        
        # Initialize DynamoDB
        if endpoint_url:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=region,
                endpoint_url=endpoint_url,
                aws_access_key_id='fakeAccessKey',
                aws_secret_access_key='fakeSecretKey'
            )
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=region)
        
        # Table names
        self.orgs_table = self.dynamodb.Table('carbontrack-organizations')
        self.teams_table = self.dynamodb.Table('carbontrack-teams')
        self.members_table = self.dynamodb.Table('carbontrack-team-members')
        self.goals_table = self.dynamodb.Table('carbontrack-team-goals')
        self.challenges_table = self.dynamodb.Table('carbontrack-challenges')
        self.participants_table = self.dynamodb.Table('carbontrack-challenge-participants')
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID with prefix"""
        return f"{prefix}_{uuid.uuid4()}"
    
    def _iso_timestamp(self) -> str:
        """Get current ISO timestamp"""
        return datetime.utcnow().isoformat()
    
    # ==================== Organization CRUD ====================
    
    def create_organization(
        self,
        name: str,
        admin_user_id: str,
        industry: str = "Other",
        size: str = "small",
        subscription_tier: str = "free"
    ) -> Dict[str, Any]:
        """
        Create a new organization
        
        Args:
            name: Organization name
            admin_user_id: User ID of the admin
            industry: Industry category
            size: Organization size (small, medium, large)
            subscription_tier: Subscription plan (free, professional, enterprise)
        
        Returns:
            Created organization data
        """
        org_id = self._generate_id("org")
        timestamp = self._iso_timestamp()
        
        organization = {
            'organization_id': org_id,
            'name': name,
            'industry': industry,
            'size': size,
            'subscription_tier': subscription_tier,
            'admin_user_id': admin_user_id,
            'settings': {
                'carbon_budget': 0,
                'reporting_frequency': 'monthly',
                'features_enabled': ['basic_tracking'],
                'branding': {}
            },
            'billing': {
                'plan': subscription_tier,
                'seats': 1,
                'renewal_date': timestamp
            },
            'metadata': {},
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active'
        }
        
        try:
            self.orgs_table.put_item(Item=organization)
            return organization
        except ClientError as e:
            raise Exception(f"Failed to create organization: {e.response['Error']['Message']}")
    
    def get_organization(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        try:
            response = self.orgs_table.get_item(Key={'organization_id': organization_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get organization: {e.response['Error']['Message']}")
    
    def update_organization(
        self,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update organization fields
        
        Args:
            organization_id: Organization ID
            updates: Dictionary of fields to update
        
        Returns:
            Updated organization data
        """
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': self._iso_timestamp()}
        expr_names = {}
        
        for key, value in updates.items():
            if key not in ['organization_id', 'created_at']:
                placeholder_key = f":val_{key.replace('.', '_')}"
                attr_name = f"#{key}"
                update_expr += f", {attr_name} = {placeholder_key}"
                expr_values[placeholder_key] = value
                expr_names[attr_name] = key
        
        try:
            response = self.orgs_table.update_item(
                Key={'organization_id': organization_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ExpressionAttributeNames=expr_names if expr_names else None,
                ReturnValues='ALL_NEW'
            )
            return response['Attributes']
        except ClientError as e:
            raise Exception(f"Failed to update organization: {e.response['Error']['Message']}")
    
    def delete_organization(self, organization_id: str) -> bool:
        """
        Delete organization (sets status to inactive)
        
        Args:
            organization_id: Organization ID
        
        Returns:
            True if successful
        """
        try:
            self.orgs_table.update_item(
                Key={'organization_id': organization_id},
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'inactive',
                    ':updated_at': self._iso_timestamp()
                }
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete organization: {e.response['Error']['Message']}")
    
    def list_user_organizations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all organizations where user is admin
        
        Args:
            user_id: User ID
        
        Returns:
            List of organizations
        """
        try:
            response = self.orgs_table.query(
                IndexName='AdminUserIndex',
                KeyConditionExpression='admin_user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list organizations: {e.response['Error']['Message']}")
    
    def list_all_organizations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all organizations (Admin only)
        
        Args:
            limit: Maximum number of organizations to return
        
        Returns:
            List of all organizations
        """
        try:
            response = self.orgs_table.scan(Limit=limit)
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list all organizations: {e.response['Error']['Message']}")
    
    def get_organization_users(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        Get all users in an organization (from team memberships)
        
        Args:
            organization_id: Organization ID
        
        Returns:
            List of unique users with their roles and teams
        """
        try:
            # Get all team members in the organization
            response = self.members_table.query(
                IndexName='OrganizationMembersIndex',
                KeyConditionExpression='organization_id = :org_id',
                ExpressionAttributeValues={':org_id': organization_id}
            )
            
            members = response.get('Items', [])
            
            # Group by user_id to get unique users with their teams
            users_map = {}
            for member in members:
                user_id = member['user_id']
                if user_id not in users_map:
                    users_map[user_id] = {
                        'user_id': user_id,
                        'organization_id': organization_id,
                        'teams': [],
                        'roles': set(),
                        'joined_at': member.get('joined_at', '')
                    }
                
                users_map[user_id]['teams'].append({
                    'team_id': member['team_id'],
                    'role': member.get('role', 'member'),
                    'permissions': member.get('permissions', [])
                })
                users_map[user_id]['roles'].add(member.get('role', 'member'))
            
            # Convert to list and clean up
            users = []
            for user_data in users_map.values():
                user_data['roles'] = list(user_data['roles'])
                user_data['team_count'] = len(user_data['teams'])
                users.append(user_data)
            
            return users
        except ClientError as e:
            raise Exception(f"Failed to get organization users: {e.response['Error']['Message']}")
    
    # ==================== Organization Statistics ====================
    
    def get_organization_stats(self, organization_id: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for an organization
        
        Args:
            organization_id: Organization ID
        
        Returns:
            Statistics dictionary
        """
        try:
            # Get all teams in organization
            teams_response = self.teams_table.query(
                IndexName='OrganizationTeamsIndex',
                KeyConditionExpression='organization_id = :org_id',
                ExpressionAttributeValues={':org_id': organization_id}
            )
            teams = teams_response.get('Items', [])
            
            # Get all members across all teams
            members_response = self.members_table.query(
                IndexName='OrganizationMembersIndex',
                KeyConditionExpression='organization_id = :org_id',
                ExpressionAttributeValues={':org_id': organization_id}
            )
            members = members_response.get('Items', [])
            
            # Calculate totals
            total_teams = len(teams)
            total_members = len(members)
            total_emissions = sum(
                float(team.get('stats', {}).get('total_emissions', 0))
                for team in teams
            )
            
            # Calculate average per member
            avg_per_member = total_emissions / total_members if total_members > 0 else 0
            
            # Get active goals
            goals_response = self.goals_table.query(
                IndexName='OrganizationGoalsIndex',
                KeyConditionExpression='organization_id = :org_id',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':org_id': organization_id,
                    ':status': 'active'
                }
            )
            active_goals = len(goals_response.get('Items', []))
            
            # Get active challenges
            challenges_response = self.challenges_table.query(
                IndexName='OrganizationChallengesIndex',
                KeyConditionExpression='organization_id = :org_id',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':org_id': organization_id,
                    ':status': 'active'
                }
            )
            active_challenges = len(challenges_response.get('Items', []))
            
            return {
                'organization_id': organization_id,
                'total_teams': total_teams,
                'total_members': total_members,
                'total_emissions': round(total_emissions, 2),
                'average_per_member': round(avg_per_member, 2),
                'active_goals': active_goals,
                'active_challenges': active_challenges,
                'teams_breakdown': [
                    {
                        'team_id': team['team_id'],
                        'name': team['name'],
                        'member_count': team.get('stats', {}).get('member_count', 0),
                        'total_emissions': team.get('stats', {}).get('total_emissions', 0),
                        'average_per_member': team.get('stats', {}).get('average_per_member', 0)
                    }
                    for team in teams
                ]
            }
        except ClientError as e:
            raise Exception(f"Failed to get organization stats: {e.response['Error']['Message']}")
    
    # ==================== Team Management ====================
    
    def create_team(
        self,
        organization_id: str,
        name: str,
        team_lead_user_id: str,
        description: str = "",
        parent_team_id: str = ""
    ) -> Dict[str, Any]:
        """Create a new team"""
        team_id = self._generate_id("team")
        timestamp = self._iso_timestamp()
        
        team = {
            'team_id': team_id,
            'organization_id': organization_id,
            'name': name,
            'description': description,
            'parent_team_id': parent_team_id,
            'team_lead_user_id': team_lead_user_id,
            'settings': {
                'carbon_budget': 0,
                'goal_period': 'quarterly',
                'visibility': 'org_only'
            },
            'stats': {
                'member_count': 0,
                'total_emissions': 0,
                'average_per_member': 0,
                'last_calculated': timestamp
            },
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active'
        }
        
        try:
            self.teams_table.put_item(Item=team)
            return team
        except ClientError as e:
            raise Exception(f"Failed to create team: {e.response['Error']['Message']}")
    
    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get team by ID"""
        try:
            response = self.teams_table.get_item(Key={'team_id': team_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get team: {e.response['Error']['Message']}")
    
    def list_organization_teams(self, organization_id: str) -> List[Dict[str, Any]]:
        """List all teams in an organization"""
        try:
            response = self.teams_table.query(
                IndexName='OrganizationTeamsIndex',
                KeyConditionExpression='organization_id = :org_id',
                ExpressionAttributeValues={':org_id': organization_id}
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list teams: {e.response['Error']['Message']}")
    
    def update_team(self, team_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update team fields"""
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': self._iso_timestamp()}
        expr_names = {}
        
        for key, value in updates.items():
            if key not in ['team_id', 'organization_id', 'created_at']:
                placeholder_key = f":val_{key.replace('.', '_')}"
                attr_name = f"#{key}"
                update_expr += f", {attr_name} = {placeholder_key}"
                expr_values[placeholder_key] = value
                expr_names[attr_name] = key
        
        try:
            response = self.teams_table.update_item(
                Key={'team_id': team_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ExpressionAttributeNames=expr_names if expr_names else None,
                ReturnValues='ALL_NEW'
            )
            return response['Attributes']
        except ClientError as e:
            raise Exception(f"Failed to update team: {e.response['Error']['Message']}")
    
    def delete_team(self, team_id: str) -> bool:
        """Delete team (sets status to archived)"""
        try:
            self.teams_table.update_item(
                Key={'team_id': team_id},
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'archived',
                    ':updated_at': self._iso_timestamp()
                }
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete team: {e.response['Error']['Message']}")
    
    # ==================== Team Membership ====================
    
    def add_team_member(
        self,
        team_id: str,
        user_id: str,
        organization_id: str,
        role: str = "member",
        invited_by: str = ""
    ) -> Dict[str, Any]:
        """Add a user to a team"""
        timestamp = self._iso_timestamp()
        
        membership = {
            'team_id': team_id,
            'user_id': user_id,
            'organization_id': organization_id,
            'role': role,
            'permissions': self._get_role_permissions(role),
            'joined_at': timestamp,
            'invited_by': invited_by,
            'status': 'active'
        }
        
        try:
            self.members_table.put_item(Item=membership)
            
            # Update team member count
            team = self.get_team(team_id)
            if team:
                member_count = team.get('stats', {}).get('member_count', 0) + 1
                self.update_team(team_id, {
                    'stats': {
                        **team.get('stats', {}),
                        'member_count': member_count
                    }
                })
            
            return membership
        except ClientError as e:
            raise Exception(f"Failed to add team member: {e.response['Error']['Message']}")
    
    def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a user from a team"""
        try:
            self.members_table.delete_item(
                Key={'team_id': team_id, 'user_id': user_id}
            )
            
            # Update team member count
            team = self.get_team(team_id)
            if team:
                member_count = max(0, team.get('stats', {}).get('member_count', 0) - 1)
                self.update_team(team_id, {
                    'stats': {
                        **team.get('stats', {}),
                        'member_count': member_count
                    }
                })
            
            return True
        except ClientError as e:
            raise Exception(f"Failed to remove team member: {e.response['Error']['Message']}")
    
    def list_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """List all members of a team"""
        try:
            response = self.members_table.query(
                KeyConditionExpression='team_id = :team_id',
                ExpressionAttributeValues={':team_id': team_id}
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list team members: {e.response['Error']['Message']}")
    
    def list_user_teams(self, user_id: str, organization_id: str = None) -> List[Dict[str, Any]]:
        """List all teams a user belongs to"""
        try:
            if organization_id:
                response = self.members_table.query(
                    IndexName='UserTeamsIndex',
                    KeyConditionExpression='user_id = :user_id AND organization_id = :org_id',
                    ExpressionAttributeValues={
                        ':user_id': user_id,
                        ':org_id': organization_id
                    }
                )
            else:
                response = self.members_table.query(
                    IndexName='UserTeamsIndex',
                    KeyConditionExpression='user_id = :user_id',
                    ExpressionAttributeValues={':user_id': user_id}
                )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list user teams: {e.response['Error']['Message']}")
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role"""
        permissions_map = {
            'member': ['view_reports', 'add_emissions'],
            'team_lead': ['view_reports', 'add_emissions', 'add_members', 'set_goals'],
            'manager': ['view_reports', 'add_emissions', 'add_members', 'set_goals', 'edit_team'],
            'admin': ['view_reports', 'add_emissions', 'add_members', 'set_goals', 'edit_team', 'delete_team']
        }
        return permissions_map.get(role, permissions_map['member'])
