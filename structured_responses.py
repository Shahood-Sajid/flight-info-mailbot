from pydantic import BaseModel,Field

class Response(BaseModel):
    Adult: int = Field(description='number of adults')
    Child: int = Field(description='number of childrens')
    Class: str = Field(description="which class the customer prefers")
    Date: str = Field(description="on which date the customer wants to their journy in dd mmm yyyy format")
    Destination: str = Field(description='3-letter IATA airport code for destination city. Examples: KHI for Karachi, LHE for Lahore, ISB for Islamabad, DXB for Dubai')
    Infant: int = Field(description='number of infants')
    StOrigin: str = Field(description='3-letter IATA airport code for origin city. Examples: KHI for Karachi, LHE for Lahore, ISB for Islamabad, DXB for Dubai')
    TripType: int = Field(description='1 if user says one way and 2 if user says roundtrip')