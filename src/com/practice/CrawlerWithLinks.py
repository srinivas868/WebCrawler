from urllib.request import urlopen

website = "https://www.nvizionsolutions.com"
openwebsite = urlopen(website)
html = openwebsite.read()

print (html)