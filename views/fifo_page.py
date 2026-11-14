from views.replacement_common import render_replacement_page


def render() -> None:
    render_replacement_page(
        "FIFO",
        "First In, First Out – the page that has been in memory the longest is replaced.",
        "Rule: keep a queue of pages in order of arrival. On a fault with all frames full, "
        "remove the page at the FRONT of the queue. A hit does not change the queue.")
