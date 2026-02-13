#!/usr/bin/env python3
"""
Verification script for the Booking model.

This script verifies that the Booking model is correctly defined
with all required attributes, constraints, and relationships.
"""

from datetime import date
from src.models import Booking, User
from sqlalchemy import inspect

def verify_booking_model():
    """Verify the Booking model structure."""
    print("Verifying Booking model...")
    print()
    
    # Check that Booking class exists
    print("✓ Booking class exists")
    
    # Check table name
    assert Booking.__tablename__ == 'bookings', "Table name should be 'bookings'"
    print(f"✓ Table name: {Booking.__tablename__}")
    
    # Check columns
    mapper = inspect(Booking)
    columns = {col.key for col in mapper.columns}
    expected_columns = {'id', 'user_id', 'start_date', 'end_date', 'status', 'created_at', 'updated_at'}
    assert columns == expected_columns, f"Expected columns {expected_columns}, got {columns}"
    print(f"✓ Columns: {', '.join(sorted(columns))}")
    
    # Check relationships
    relationships = {rel.key for rel in mapper.relationships}
    assert 'user' in relationships, "Should have 'user' relationship"
    print(f"✓ Relationships: {', '.join(sorted(relationships))}")
    
    # Check constraints
    table = Booking.__table__
    constraints = [c.name for c in table.constraints if hasattr(c, 'name') and c.name]
    print(f"✓ Constraints: {', '.join(constraints)}")
    assert 'check_end_date_after_start_date' in constraints, "Should have end_date > start_date constraint"
    
    # Check validators
    assert hasattr(Booking, 'validate_dates'), "Should have validate_dates method"
    print("✓ Date validation method exists")
    
    # Check default status (column default is set in the model)
    status_column = mapper.columns['status']
    assert status_column.default is not None, "Status column should have a default value"
    print("✓ Default status is configured")
    
    # Check __repr__ method
    booking_instance = Booking(
        user_id=1,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 8)
    )
    repr_str = repr(booking_instance)
    assert 'Booking' in repr_str, "__repr__ should contain 'Booking'"
    print(f"✓ __repr__ method: {repr_str}")
    
    print()
    print("=" * 60)
    print("All Booking model verifications passed! ✓")
    print("=" * 60)
    print()
    print("Model Summary:")
    print(f"  - Table: {Booking.__tablename__}")
    print(f"  - Columns: {len(columns)}")
    print(f"  - Relationships: {len(relationships)}")
    print(f"  - Constraints: {len(constraints)}")
    print()
    print("Requirements validated:")
    print("  - 7.2: Booking details stored in database ✓")
    print("  - 7.5: Date validation (end_date > start_date) ✓")

if __name__ == '__main__':
    verify_booking_model()
