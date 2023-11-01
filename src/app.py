import pathlib
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from wordcloud import WordCloud
import base64
import io
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

app = Dash(__name__, title="ZimElectionsApp")

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# def load_data(data_file: str) -> pd.DataFrame:
#     '''
#     Load data from /data directory
#     '''
#     PATH = pathlib.Path(__file__).parent
#     DATA_PATH = PATH.joinpath("data").resolve()
#     return pd.read_csv(DATA_PATH.joinpath(data_file))

#Load the CSV data into a Pandas DataFrame
df = pd.read_csv('assets/Elections.csv')

# df = load_data('Elections.csv')

# Convert the 'Timestamp' column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Convert the 'Text' column to strings
df['Text'] = df['Text'].astype(str)

# Convert the 'Likes' and 'Retweets' columns to numeric data type
df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce')
df['Retweets'] = pd.to_numeric(df['Retweets'], errors='coerce')

# Initialize the Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create the layout of the dashboard
app.layout = dbc.Container(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H1("Zimbabwe Elections Dashboard", className="navbar-brand"))
                            ],
                            align="center",
                            style={"margin": 0}  # Remove horizontal margins
                        ),
                    ),
                ],
                fluid=True,
                style={"padding": 0}  # Remove vertical padding
            ),
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.Label('Select Date Range'),
                    dcc.DatePickerRange(
                        id='date-picker',
                        start_date=df['Timestamp'].min().date(),
                        end_date=df['Timestamp'].max().date(),
                        className='mb-2',
                        style={'display': 'flex', 'justify-content': 'center'}
                    )
                ],
                width={'size': 4, 'offset': 0}
            ),
            justify='center',
            className='mt-4'
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H2('Trending Topics for the day', className='text-center'),
                    html.Img(id='word-cloud-image', className='img-fluid mx-auto d-block')
                ],
                width=12
            ),
            className='mt-4'
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='verified-graph', style={'height': '400px'}),
                width=12
            ),
            className='mt-4'
        ),
        dbc.Row(
            dbc.Col(
                html.H2('Top 10 Most Popular Tweets', className='text-center mb-4')
            ),
            justify='center'
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='top-tweets-table',
                    columns=[
                        {'name': 'Twitter Handle', 'id': 'Twitter Handle'},
                        {'name': 'Text', 'id': 'Text'},
                        {'name': 'Likes', 'id': 'Likes'},
                        {'name': 'Retweets', 'id': 'Retweets'}
                    ],
                    style_cell={'textAlign': 'left'},
                    style_data={'whiteSpace': 'normal'},
                    style_table={'maxWidth': '1200px', 'margin': '40px auto'}
                ),
                width=12
            ),
            className='mt-4'
        ),
    ],
    className='mt-5'
)

# Define a function to generate the word cloud
def generate_word_cloud(date):
        # Define the words to be excluded from the WordCloud
    stopwords = [
    'Zimbabwe', 'ZimDecides2023', 'ZimbabweDecides', 'ElectionsZW', 'ZimDecides', 'this', "they're", "They've", 'I', 'asi','a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in',
    'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with', 'what', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'if', 'iff', 'whether', 'unless', 'until', 'not', 'they', 'there', 'or', 'so', 'we', 'who', 'should', 'here', 'their'
    , 'no', 'their', 'those', 'got', 'also', 'but', "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz",
]
    filtered_df = df[(df['Timestamp'].dt.date >= date[0]) & (df['Timestamp'].dt.date <= date[1])]  # Filter data by date range
    text = ' '.join(filtered_df['Text'])  # Concatenate all text entries for the selected date range
    word_cloud = WordCloud(
        background_color='white',  # Set the background color to white
        colormap='tab10',  # Use a gray color scheme
        stopwords=stopwords,
        width=1200, height=300
    ).generate(text)
    image_bytes = io.BytesIO()  # Convert the PIL Image to bytes
    word_cloud.to_image().save(image_bytes, format='PNG')
    return image_bytes.getvalue()

# Define a callback function to update the word cloud image, the verified user graph, and the top tweets table based on the selected date range
@app.callback(
    [Output('word-cloud-image', 'src'), Output('verified-graph', 'figure'), Output('top-tweets-table', 'data')],
    [Input('date-picker', 'start_date'), Input('date-picker', 'end_date')]
)
def update_word_cloud_graph_and_table(start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    filtered_df = df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)]  # Filter data by date range

    # Generate word cloud image
    word_cloud_image = generate_word_cloud([start_date, end_date])

    # Calculate the count of verified and non-verified users
    verified_counts = filtered_df['Verified'].value_counts()

    # Create a bar chart for verified users
    verified_graph = go.Figure(data=[go.Bar(x=verified_counts.index, y=verified_counts.values)])
    verified_graph.update_layout(title='Verified Users', xaxis_title='Verified', yaxis_title='Count')

    # Get the top 10 most popular tweets
    top_tweets = filtered_df.nlargest(10, 'Retweets')[['Twitter Handle', 'Text', 'Likes', 'Retweets']].to_dict('records')

    return f'data:image/png;base64,{base64.b64encode(word_cloud_image).decode()}', verified_graph, top_tweets

# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True, port= 8060)