def format_money(amount: float, currency: str = "UZS") -> str:
    """
    Formats monetary values cleanly.
    Example: 1500000 UZS -> 1 500 000 so'm
    """
    formatted = f"{amount:,.2f}"
    # Convert standard comma grouping to spaces: "1,500,000.00" -> "1 500 000.00"
    formatted = formatted.replace(",", " ")
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
        
    currency_label = "so'm" if currency.upper() == "UZS" else currency.upper()
    return f"{formatted} {currency_label}"
