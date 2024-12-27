# ao3-tag-wrapped
AO3 Tag Wrapped read through pages of a specific AO3 tag and constructs a summary what the community that uses said tag has achieved. This works for all tags (even uncategorized tags).

Credit: AO3 Tag Wrapped is built largely based on the original AO3 Wrapped by soupbanana & Zịt & Luna which can be found <a href="https://colab.research.google.com/drive/1GhhENZ8RjRWKgwIchqRS-KllPF8AEci_?usp=sharing">here</a>

<h2>Online Version (No Installing Required):</h2>
Go to <a href="https://colab.research.google.com/drive/1CnJcZD-yL4a9jIv1WKMDZFSu0TzDEs1c?usp=sharing">this Google Colab project</a>.

<h2>Offline Version (for Windows only. I am not familiar with MacOs, but these steps are easy enough that you can search up how to do them online):</h2>

1. Download the <i>ao3_tag_wrapped.py file</i>
2. Make sure that you have Python installed. You can check if you've already have Python by opening Command Prompt on your machine and typing `py --version`.
3. Make sure that you have pip installed. You can check if you've already have Python by typing `pip --version`
4. Install Mechanize package by typing `pip install mechanize`
5. Install BeautifulSoup package by typing `pip install beautifulsoup4`
6. Install Numpy by typing `pip install numpy`
7. Move to the folder that contains the the ao3_tag_wrapped.py file using `cd (folder address)` and type `python ao3_tag_wrapped.py`

After step 7, the program will ask you for your <ins>username</ins>, <ins>password</ins>, the <ins>year</ins> you want to fetch data for, and a <ins>link to the main page of the tag</ins> you want to run this on. Please enter your username and password as they are. <ins>Enter one year only</ins>.

<h3>Why logging in?</h3>
It is possible to view works that belong to a tag without having to log in. However, logging in allows you to see works that are only visible to someone with an account.

<h2>How to get the required link:</h2>

1. Go to the tag's page on ao3.
2. Copy the link to that page and paste it. Make sure that:
   - you don't put any filter onto the tag
   - your link <ins>contains the prefix "https://"</ins>
   - your link <ins>DOESN'T have the suffix "?page=1".</ins>

The content will be written to a <i>.csv file</i> in the same folder.
