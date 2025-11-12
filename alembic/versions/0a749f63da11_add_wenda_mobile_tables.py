"""add_wenda_mobile_tables

Revision ID: 0a749f63da11
Revises: d88ab493f030
Create Date: 2025-11-12 10:18:43.756663

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '0a749f63da11'
down_revision = 'd88ab493f030'
branch_labels = None
depends_on = None


def upgrade():
    # 1. CREATE CATEGORIES TABLE
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('slug', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_slug', 'categories', ['slug'])
    op.create_index('idx_display_order', 'categories', ['display_order'])

    # 2. ADD NEW COLUMNS TO USERS TABLE
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('apple_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true'))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_google_id', 'users', ['google_id'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

    # 3. ADD NEW COLUMNS TO DESTINATIONS TABLE
    op.add_column('destinations', sa.Column('slug', sa.String(200), nullable=True))
    op.add_column('destinations', sa.Column('long_description', sa.Text(), nullable=True))
    op.add_column('destinations', sa.Column('location', sa.String(100), nullable=True))
    op.add_column('destinations', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('destinations', sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('destinations', sa.Column('opening_hours', sa.String(200), nullable=True))
    op.add_column('destinations', sa.Column('ticket_price', sa.String(100), nullable=True))
    op.add_column('destinations', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('destinations', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('destinations', sa.Column('website', sa.String(500), nullable=True))
    op.add_column('destinations', sa.Column('amenities', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('destinations', sa.Column('accessibility', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('destinations', sa.Column('rating', sa.DECIMAL(2, 1), server_default='0.0'))
    op.add_column('destinations', sa.Column('review_count', sa.Integer(), server_default='0'))
    op.add_column('destinations', sa.Column('view_count', sa.Integer(), server_default='0'))
    op.add_column('destinations', sa.Column('is_featured', sa.Boolean(), server_default='false'))
    op.add_column('destinations', sa.Column('is_active', sa.Boolean(), server_default='true'))
    op.add_column('destinations', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('destinations', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    op.create_foreign_key('fk_destinations_category', 'destinations', 'categories', ['category_id'], ['id'], ondelete='RESTRICT')
    op.create_index('idx_dest_slug', 'destinations', ['slug'], unique=True)
    op.create_index('idx_dest_category', 'destinations', ['category_id'])
    op.create_index('idx_dest_rating', 'destinations', ['rating'])
    op.create_index('idx_dest_featured', 'destinations', ['is_featured'])
    op.create_index('idx_dest_province_category', 'destinations', ['province', 'category_id'])

    # 4. CREATE DESTINATION_IMAGES TABLE
    op.create_table(
        'destination_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('destination_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('thumbnail_url', sa.String(500), nullable=False),
        sa.Column('caption', sa.String(200), nullable=True),
        sa.Column('is_main', sa.Boolean(), server_default='false'),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE')
    )
    op.create_index('idx_dest_img_destination', 'destination_images', ['destination_id'])
    op.create_index('idx_dest_img_main', 'destination_images', ['destination_id', 'is_main'])

    # 5. CREATE REVIEWS TABLE
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('destination_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('helpful_count', sa.Integer(), server_default='0'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'destination_id', name='unique_user_destination')
    )
    op.create_index('idx_reviews_user', 'reviews', ['user_id'])
    op.create_index('idx_reviews_destination', 'reviews', ['destination_id'])
    op.create_index('idx_reviews_rating', 'reviews', ['rating'])
    op.create_index('idx_reviews_created', 'reviews', ['created_at'])

    # 6. CREATE REVIEW_IMAGES TABLE
    op.create_table(
        'review_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('thumbnail_url', sa.String(500), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE')
    )
    op.create_index('idx_review_img_review', 'review_images', ['review_id'])

    # 7. CREATE REVIEW_HELPFUL TABLE
    op.create_table(
        'review_helpful',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('review_id', 'user_id', name='unique_review_user_helpful')
    )
    op.create_index('idx_helpful_review', 'review_helpful', ['review_id'])
    op.create_index('idx_helpful_user', 'review_helpful', ['user_id'])

    # 8. CREATE FAVORITES TABLE
    op.create_table(
        'favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('destination_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'destination_id', name='unique_user_dest_favorite')
    )
    op.create_index('idx_fav_user', 'favorites', ['user_id'])
    op.create_index('idx_fav_destination', 'favorites', ['destination_id'])
    op.create_index('idx_fav_created', 'favorites', ['created_at'])

    # 9. CREATE TRIPS TABLE
    op.create_table(
        'trips',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default='upcoming'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('end_date >= start_date', name='check_trip_dates'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('idx_trips_user', 'trips', ['user_id'])
    op.create_index('idx_trips_status', 'trips', ['status'])
    op.create_index('idx_trips_dates', 'trips', ['start_date', 'end_date'])

    # 10. CREATE TRIP_DESTINATIONS TABLE
    op.create_table(
        'trip_destinations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('destination_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('visit_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('trip_id', 'destination_id', name='unique_trip_dest')
    )
    op.create_index('idx_trip_dest_trip', 'trip_destinations', ['trip_id'])
    op.create_index('idx_trip_dest_destination', 'trip_destinations', ['destination_id'])

    # 11. CREATE USER_PREFERENCES TABLE
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('language', sa.String(5), server_default='pt'),
        sa.Column('notifications_enabled', sa.Boolean(), server_default='true'),
        sa.Column('email_notifications', sa.Boolean(), server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), server_default='true'),
        sa.Column('favorite_categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('theme', sa.String(10), server_default='light'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('idx_user_pref_user', 'user_preferences', ['user_id'])

    # 12. CREATE PASSWORD_RESETS TABLE
    op.create_table(
        'password_resets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_pwd_reset_email', 'password_resets', ['email'])
    op.create_index('idx_pwd_reset_token', 'password_resets', ['token'])
    op.create_index('idx_pwd_reset_expires', 'password_resets', ['expires_at'])

    # 13. INSERT INITIAL CATEGORIES
    op.execute("""
        INSERT INTO categories (name, slug, description, icon, color, display_order) VALUES
        ('Natural', 'natural', 'Praias, montanhas, parques e natureza', 'leaf', '#10B981', 1),
        ('Cultural', 'cultural', 'Museus, galerias, centros culturais', 'palette', '#8B5CF6', 2),
        ('Histórico', 'historical', 'Monumentos, fortalezas, sítios históricos', 'book', '#F59E0B', 3),
        ('Aventura', 'adventure', 'Esportes radicais, trilhas, atividades', 'rocket', '#EF4444', 4)
    """)


def downgrade():
    # Drop tables in reverse order
    op.drop_table('password_resets')
    op.drop_table('user_preferences')
    op.drop_table('trip_destinations')
    op.drop_table('trips')
    op.drop_table('favorites')
    op.drop_table('review_helpful')
    op.drop_table('review_images')
    op.drop_table('reviews')
    op.drop_table('destination_images')
    
    # Drop new columns from destinations
    op.drop_constraint('fk_destinations_category', 'destinations', type_='foreignkey')
    op.drop_column('destinations', 'deleted_at')
    op.drop_column('destinations', 'updated_at')
    op.drop_column('destinations', 'is_active')
    op.drop_column('destinations', 'is_featured')
    op.drop_column('destinations', 'view_count')
    op.drop_column('destinations', 'review_count')
    op.drop_column('destinations', 'rating')
    op.drop_column('destinations', 'accessibility')
    op.drop_column('destinations', 'amenities')
    op.drop_column('destinations', 'website')
    op.drop_column('destinations', 'email')
    op.drop_column('destinations', 'phone')
    op.drop_column('destinations', 'ticket_price')
    op.drop_column('destinations', 'opening_hours')
    op.drop_column('destinations', 'category_id')
    op.drop_column('destinations', 'address')
    op.drop_column('destinations', 'location')
    op.drop_column('destinations', 'long_description')
    op.drop_column('destinations', 'slug')
    
    # Drop new columns from users
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'apple_id')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'avatar_url')
    
    # Drop categories table
    op.drop_table('categories')
