from views.replacement_common import render_replacement_page


def render() -> None:
    render_replacement_page(
        "LRU",
        "Least Recently Used – the page that has not been used for the longest time is replaced.",
        "Rule: remember when each page was last used. On a fault with all frames full, remove the "
        "page whose last use is OLDEST. Every access (hit or fault) refreshes a page's recency.")
