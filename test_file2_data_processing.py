"""
Data Processing Pipeline Example
ETL system with data validation and transformation
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
import json


class DataFormat(Enum):
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"


@dataclass
class DataRow:
    """Single data row"""
    data: Dict[str, Any]
    source: str
    timestamp: datetime
    valid: bool = True
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class DataSchema:
    """Data schema definition"""

    def __init__(self, fields: Dict[str, type]):
        self.fields = fields
        self.required_fields = list(fields.keys())

    def validate(self, row: DataRow) -> DataRow:
        """Validate a data row against schema"""
        errors = []

        # Check required fields
        for field in self.required_fields:
            if field not in row.data:
                errors.append(f"Missing required field: {field}")

        # Check data types
        for field, expected_type in self.fields.items():
            if field in row.data:
                value = row.data[field]
                if not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {field}: expected {expected_type.__name__}")

        if errors:
            row.valid = False
            row.errors.extend(errors)

        return row


class DataSource(ABC):
    """Abstract data source"""

    @abstractmethod
    def read(self) -> List[DataRow]:
        pass


class FileDataSource(DataSource):
    """File-based data source"""

    def __init__(self, file_path: str, format: DataFormat):
        self.file_path = file_path
        self.format = format

    def read(self) -> List[DataRow]:
        rows = []
        try:
            if self.format == DataFormat.JSON:
                rows = self._read_json()
            elif self.format == DataFormat.CSV:
                rows = self._read_csv()
        except Exception as e:
            print(f"Error reading {self.file_path}: {e}")
        return rows

    def _read_json(self) -> List[DataRow]:
        rows = []
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            for item in data:
                row = DataRow(item, self.file_path, datetime.now())
                rows.append(row)
        return rows

    def _read_csv(self) -> List[DataRow]:
        rows = []
        # Simplified CSV reading
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[1:], 1):  # Skip header
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    row_data = {
                        "id": int(parts[0]),
                        "name": parts[1],
                        "value": float(parts[2]) if len(parts) > 2 else 0.0
                    }
                    row = DataRow(row_data, self.file_path, datetime.now())
                    rows.append(row)
        return rows


class DataTransformer(ABC):
    """Abstract data transformer"""

    @abstractmethod
    def transform(self, row: DataRow) -> DataRow:
        pass


class FilterTransformer(DataTransformer):
    """Filter rows based on conditions"""

    def __init__(self, condition: Callable[[Dict[str, Any]], bool]):
        self.condition = condition

    def transform(self, row: DataRow) -> DataRow:
        if not self.condition(row.data):
            row.valid = False
            row.errors.append("Row filtered out")
        return row


class EnrichmentTransformer(DataTransformer):
    """Add computed fields"""

    def transform(self, row: DataRow) -> DataRow:
        # Add computed fields
        if "value" in row.data:
            row.data["value_category"] = self._categorize_value(row.data["value"])
            row.data["processed_at"] = datetime.now()
        return row

    def _categorize_value(self, value: float) -> str:
        if value < 10:
            return "low"
        elif value < 100:
            return "medium"
        else:
            return "high"


class DataValidator:
    """Data validation"""

    def __init__(self, schema: DataSchema):
        self.schema = schema

    def validate_batch(self, rows: List[DataRow]) -> List[DataRow]:
        validated = []
        for row in rows:
            validated_row = self.schema.validate(row)
            validated.append(validated_row)
        return validated


class DataSink(ABC):
    """Abstract data sink"""

    @abstractmethod
    def write(self, rows: List[DataRow]) -> bool:
        pass


class DatabaseSink(DataSink):
    """Database data sink"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def write(self, rows: List[DataRow]) -> bool:
        valid_rows = [r for r in rows if r.valid]
        try:
            print(f"Writing {len(valid_rows)} rows to database")
            # Simulate database write
            return True
        except Exception as e:
            print(f"Error writing to database: {e}")
            return False


class FileSink(DataSink):
    """File data sink"""

    def __init__(self, file_path: str, format: DataFormat):
        self.file_path = file_path
        self.format = format

    def write(self, rows: List[DataRow]) -> bool:
        valid_rows = [r for r in rows if r.valid]
        try:
            with open(self.file_path, 'w') as f:
                if self.format == DataFormat.JSON:
                    data = [r.data for r in valid_rows]
                    json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing to {self.file_path}: {e}")
            return False


class DataPipeline:
    """ETL Pipeline"""

    def __init__(self, source: DataSource, transformers: List[DataTransformer],
                 validator: DataValidator, sink: DataSink):
        self.source = source
        self.transformers = transformers
        self.validator = validator
        self.sink = sink

    def run(self) -> Dict[str, Any]:
        """Run the complete pipeline"""
        print("Starting ETL pipeline...")

        # Extract
        print("Extracting data...")
        raw_data = self.source.read()
        print(f"Extracted {len(raw_data)} rows")

        # Transform
        print("Transforming data...")
        transformed_data = raw_data.copy()
        for transformer in self.transformers:
            transformed_data = [transformer.transform(row) for row in transformed_data]

        # Validate
        print("Validating data...")
        validated_data = self.validator.validate_batch(transformed_data)
        valid_count = sum(1 for r in validated_data if r.valid)
        print(f"Valid rows: {valid_count}/{len(validated_data)}")

        # Load
        print("Loading data...")
        success = self.sink.write(validated_data)

        return {
            "total_rows": len(raw_data),
            "valid_rows": valid_count,
            "success": success,
            "timestamp": datetime.now()
        }


# Example usage
if __name__ == "__main__":
    # Create schema
    schema = DataSchema({
        "id": int,
        "name": str,
        "value": float
    })

    # Create pipeline components
    source = FileDataSource("input.json", DataFormat.JSON)
    filter_transformer = FilterTransformer(lambda x: x.get("value", 0) > 0)
    enrichment_transformer = EnrichmentTransformer()
    validator = DataValidator(schema)
    sink = DatabaseSink("postgresql://localhost/db")

    # Run pipeline
    pipeline = DataPipeline(
        source=source,
        transformers=[filter_transformer, enrichment_transformer],
        validator=validator,
        sink=sink
    )

    result = pipeline.run()
    print(f"Pipeline completed: {result}")