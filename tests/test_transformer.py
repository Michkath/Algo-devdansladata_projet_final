import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cleaning import DataTransformer

@pytest.fixture
def transformer():
    return DataTransformer()

def test_apply_cleaning_rules_logic(transformer):
    """Test Unitaire : Vérifie la transformation des types et valeurs."""
  
    test_data = {
        # Ici, les deux premières lignes sont strictement identiques
        'NOM COMMERCIAL': ['Hôtel A', 'Hôtel A', 'Hôtel B'], 
        'NOMBRE DE CHAMBRES': ['10', '10', '5'],
        'DATE DE CLASSEMENT': ['01/01/2023', '01/01/2023', 'invalid_date']
    }
    df = pd.DataFrame(test_data)
    
    cleaned_df = transformer.clean_dataframe(df)
    
    # Test Doublons
    assert len(cleaned_df) == 2 
    
    # Test Conversion Numérique (le "-" doit devenir 0 via notre fillna)
    assert cleaned_df['NOMBRE DE CHAMBRES'].iloc[1] == 5
    assert cleaned_df['NOMBRE DE CHAMBRES'].dtype in [np.float64, np.int64]
    
    # Test Dates
    assert pd.isna(cleaned_df['DATE DE CLASSEMENT'].iloc[1])