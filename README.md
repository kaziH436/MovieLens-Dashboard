# MovieLens Dashboard

Interactive Streamlit app for GroupLens MovieLens 100K ratings. It answers four questions:

1. **Genre breakdown** — unique rated movies per genre (horizontal bars).
2. **Genre satisfaction** — highest and lowest average ratings by genre.
3. **Ratings over time** — mean rating by movie **release** year (`year`, not `rating_year`).
4. **Best movies with a floor** — top 5 titles with at least N ratings (try 50, then 150).

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Main file for Streamlit Community Cloud: `app.py` on branch `main`.

## Deploy (Streamlit Community Cloud)

1. Push this repo to public GitHub (`<username>/MovieLens-Dashboard`).
2. Open [https://share.streamlit.io](https://share.streamlit.io), connect GitHub, and create an app.
3. Repository: `<username>/MovieLens-Dashboard`, branch `main`, main file path `app.py`.
4. Deploy. The live URL will look like `https://<app-name>.streamlit.app`.

Process notes for the course writeup live in [BUILD_LOG.md](BUILD_LOG.md).
