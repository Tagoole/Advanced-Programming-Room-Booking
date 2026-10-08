@dataclass(frozen=True, slots=True)
class BookingReference:
    value: str

    def __post_init__(self):
        cleaned = self.value.strip().upper()

        if not cleaned:
            raise ValueError("Booking reference cannot be empty")
        if not re.match(r"^BK-\d{4,}$", cleaned):
            raise ValueError(
                f"Invalid booking reference format: {self.value}. "
                "Expected something like BK-1001"
            )
        object.__setattr__(self, "value", cleaned)

    @classmethod
    def create(cls, value: str) -> "BookingReference":
        return cls(value)

    def __str__(self) -> str:
        return self.value
