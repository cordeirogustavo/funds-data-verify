#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fund Data Verification Script

This script reads fund data from an Excel file, validates it against
external APIs and generates a new Excel file with validation results.
"""

import os
import re
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime

class FundDataVerifier:
    """Process fund data and verify against external APIs."""

    INPUT_PATH = Path("application/documents/entrada.xlsx")
    OUTPUT_PATH = Path("application/documents/planilha-validada.xlsx")
    
    FUNDSNET_API = "http://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
    MZIQ_API = f"{os.getenv('MZ_IQ_FUNDS_DATA_URL')}/hash"

    def __init__(self):
        """Initialize the fund data verifier."""
        self.data = None

    def normalize_cnpj(self, cnpj):
        """Remove special characters from CNPJ."""
        if not cnpj or pd.isna(cnpj):
            return ""
        return re.sub(r'[./-]', '', str(cnpj))

    def read_input_file(self):
        """Read the input Excel file."""
        try:
            self.data = pd.read_excel(self.INPUT_PATH)
            print(f"Successfully read {len(self.data)} rows from {self.INPUT_PATH}")
            return True
        except Exception as e:
            print(f"Error reading input file: {e}")
            return False

    def query_fundsnet(self, cnpj):
        """Query the FundsNet API for fund data."""
        if not cnpj or pd.isna(cnpj):
            return None, None, None
        try:
            query = {"cnpj": cnpj, "cnpjFundo": cnpj, "idCategoria": 0, "idTipoDocumento": 0, "d": 2, "s": 0, "l": 10, "o[0][dataEntrega]": "desc", "idEspecieDocumento": 0}
            response = requests.get(self.FUNDSNET_API, params=query, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data and len(data) > 0:
                    fund_info = data[0]
                    return fund_info.get("descricaoFundo"), fund_info.get("dataEntrega"), fund_info.get("id")
            
            return None, None, None
        except Exception as e:
            print(f"Error querying FundsNet for CNPJ {cnpj}: {e}")
            return None, None

    def query_mziq(self, fund_name):
        """Query the MZiQ API for fund ID."""
        if not fund_name or pd.isna(fund_name):
            return None
            
        try:
            params = {"fundName": fund_name}
            response = requests.get(self.MZIQ_API, params=params, timeout=10, headers={"mz-internal-app": os.getenv("MZ_IQ_API_KEY")})
            
            if response.status_code == 200:
                data = response.json()
                return data.get("id")
            
            return None
        except Exception as e:
            print(f"Error querying MZiQ for fund name {fund_name}: {e}")
            return None

    def format_date(self, date_str):
        """Format date string."""
        if not date_str or pd.isna(date_str):
            return ""
            
        try:
            # Handle ISO format date strings like "2024-12-01T00:00:00"
            return date_str.split("T")[0] if "T" in date_str else date_str
        except Exception:
            return date_str

    def process_data(self):
        """Process each row in the dataframe."""
        if self.data is None:
            print("No data loaded. Please run read_input_file first.")
            return False
            
        # Add new columns
        self.data["validado"] = False
        self.data["dataUltimoArquivamento"] = ""
        self.data["externalId"] = ""
        self.data["idRedis"] = ""
        
        for idx, row in self.data.iterrows():
            cnpj = row.get("CNPJ")
            print(f"Processing row {idx+1}/{len(self.data)}: CNPJ={cnpj}")
            
            try:
                # Query FundsNet
                fund_name, last_delivery_date, external_id = self.query_fundsnet(cnpj)
                
                if fund_name:
                    # Query MZiQ
                    fund_id = self.query_mziq(fund_name)
                    print(f"Fund ID REDIS: {fund_id}")
                    
                    # Update dataframe
                    self.data.at[idx, "dataUltimoArquivamento"] = last_delivery_date
                    self.data.at[idx, "idRedis"] = fund_id if fund_id else ""
                    self.data.at[idx, "externalId"] = external_id if external_id else ""
                    # Validate
                    normalized_cnpj = self.normalize_cnpj(cnpj)
                    print(f"Normalized CNPJ: {normalized_cnpj}")
                    self.data.at[idx, "validado"] = (fund_id == normalized_cnpj) if fund_id else False
            
            except Exception as e:
                print(f"Error processing row {idx+1}: {e}")
                # Continue with next row
        
        return True

    def save_output_file(self):
        """Save the processed data to a new Excel file."""
        if self.data is None:
            print("No data processed. Please run process_data first.")
            return False
            
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.OUTPUT_PATH), exist_ok=True)
            
            # Write to Excel
            self.data.to_excel(self.OUTPUT_PATH, index=False)
            print(f"Results saved to {self.OUTPUT_PATH}")
            return True
        except Exception as e:
            print(f"Error saving output file: {e}")
            return False

    def run(self):
        """Run the full verification process."""
        if not self.read_input_file():
            return False
        
        if not self.process_data():
            return False
        
        return self.save_output_file()


def main():
    """Execute the fund data verification process."""
    verifier = FundDataVerifier()
    success = verifier.run()
    
    if success:
        print("Fund data verification completed successfully.")
    else:
        print("Fund data verification failed.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 