"""
data_reader.py

Conversão dos dados recebidos pela API para valores numéricos.
"""

class DataReader:

    @staticmethod
    def parse_component(text):
        text = str(text).strip().lower().replace(" ", "")

        if text.endswith("G"):
            return float(text[:-1]) * 1e9
        
        if text.endswith("M"):
                    return float(text[:-1]) * 1e6
        
        if text.endswith("m"):
            return float(text[:-1]) * 1e-3

        if text.endswith("k"):
            return float(text[:-1]) * 1e3

        if text.endswith("u"):
            return float(text[:-1]) * 1e-6

        if text.endswith("n"):
            return float(text[:-1]) * 1e-9

        if text.endswith("p"):
            return float(text[:-1]) * 1e-12

        return float(text)
