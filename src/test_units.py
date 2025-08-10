import unittest
import os
from . import db_manager
from db.database_setup import setup_database

class TestUnits(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for unit tests."""
        cls.db_path = 'db/test_units.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)

    def setUp(self):
        """Clean the unit tables before each test."""
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM compound_units;")
        cursor.execute("DELETE FROM units;")
        # Re-populate defaults for clean state
        default_units = [('Pcs',), ('Nos',), ('Box',), ('Dozen',)]
        cursor.executemany("INSERT OR IGNORE INTO units (name) VALUES (?)", default_units)
        conn.commit()
        conn.close()

    def test_add_and_get_simple_unit(self):
        """Test that a simple unit can be added and all units can be retrieved."""
        initial_units = db_manager.get_all_units()
        self.assertEqual(len(initial_units), 4)

        result = db_manager.add_unit("Kg")
        self.assertTrue(result)

        all_units = db_manager.get_all_units()
        self.assertEqual(len(all_units), 5)
        self.assertTrue(any(unit['name'] == 'Kg' for unit in all_units))

    def test_add_duplicate_simple_unit(self):
        """Test that adding a duplicate unit name fails."""
        result = db_manager.add_unit("Box")
        self.assertFalse(result) # Should fail because 'Box' already exists

    def test_add_and_get_compound_unit(self):
        """Test that a compound unit relationship can be added and retrieved."""
        units = {unit['name']: unit['id'] for unit in db_manager.get_all_units()}
        box_id = units.get('Box')
        pcs_id = units.get('Pcs')

        self.assertIsNotNone(box_id)
        self.assertIsNotNone(pcs_id)

        result = db_manager.add_compound_unit(box_id, pcs_id, 10.0)
        self.assertTrue(result)

        compound_units = db_manager.get_all_compound_units_display()
        self.assertEqual(len(compound_units), 1)

        c_unit = compound_units[0]
        self.assertEqual(c_unit['base_unit_name'], 'Box')
        self.assertEqual(c_unit['secondary_unit_name'], 'Pcs')
        self.assertEqual(c_unit['conversion_factor'], 10.0)

if __name__ == '__main__':
    unittest.main()
