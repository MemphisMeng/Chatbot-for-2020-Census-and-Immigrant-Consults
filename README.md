---


---

<h1 id="welcome-to-resiliency-challenge">Welcome to Resiliency Challenge!</h1>
<p>In this hackathon, we are going to develop an AI-based chatbot on Facebook messenger and Whatsapp, which is expected to propagate the information of 2020 US Census and COVID-19 to everyone in need, especially the non English speaking immigrants.</p>
<h2 id="requirement">Requirement</h2>
<p>Python3.6</p>
<p>Flask==1.1.2</p>
<p>ymessenger==0.0.7.0</p>
<p>nltk</p>
<p>pandas</p>
<p>sklearn</p>
<p>heroku</p>
<h2 id="tutorial">Tutorial</h2>
<ol>
<li>Install <a href="%5Bhttps://devcenter.heroku.com/articles/heroku-cli#download-and-install%5D(https://devcenter.heroku.com/articles/heroku-cli#download-and-install)">heroku</a></li>
</ol>
<blockquote>
<p>Example (Ubuntu)</p>
</blockquote>
<pre><code>
$ sudo snap install --classic heroku

</code></pre>
<ol start="2">
<li><a href="%5Bhttps://devcenter.heroku.com/articles/heroku-cli#getting-started%5D(https://devcenter.heroku.com/articles/heroku-cli#getting-started)">Login heroku account</a></li>
</ol>
<pre><code>
$ heroku login

</code></pre>
<ol start="3">
<li><a href="%5Bhttps://devcenter.heroku.com/articles/creating-apps#creating-a-named-app%5D(https://devcenter.heroku.com/articles/creating-apps#creating-a-named-app)">Create a heorku app</a></li>
</ol>
<pre><code>
$ heroku create example

</code></pre>
<ol start="4">
<li>
<p>Setup a <a href="https://developers.facebook.com/">Facebook application</a> in the developer</p>
</li>
<li>
<p>Add a messenger product in the application</p>
</li>
</ol>
<p><img src="https://github.com/jeanmidevacc/messenger-bot-python-flask-zappa-amazon/blob/master/pictures/setup_app.png" alt="alt text"></p>
<ol start="6">
<li>Create a Facebook page</li>
</ol>
<p><img src="https://github.com/MemphisMeng/Chatbot-for-2020-Census-and-Immigrant-Consults/blob/master/images/setup_app.png" alt="alt text"></p>
<ol start="7">
<li>
<p>On the developer platform, click the “Generate Token” and copy the token for further use<img src="https://github.com/MemphisMeng/Chatbot-for-2020-Census-and-Immigrant-Consults/blob/master/images/ACCESS_TOKEN.png" alt="alt text"></p>
</li>
<li>
<p>On the settings tab of the app that you created, click “Config Vars”<img src="https://github.com/MemphisMeng/Chatbot-for-2020-Census-and-Immigrant-Consults/blob/master/images/Config_vars.png" alt="enter image description here"></p>
</li>
<li>
<p>Set two variables, ACCESS_TOKEN=&lt;the  token  you  copy  in  the  developer  platform&gt;, VERFIY_TOKEN=&lt;CUSTOMIZED&gt;(make sure its length is between 16 and 32)<img src="https://github.com/MemphisMeng/Chatbot-for-2020-Census-and-Immigrant-Consults/blob/master/images/vars.png" alt="enter image description here"></p>
</li>
<li>
<p><a href="https://devcenter.heroku.com/articles/git#prerequisites-install-git-and-the-heroku-cli">Deploy</a> this project on the heroku end of your account</p>
</li>
</ol>
<pre><code>
$ git init

$ git add .

$ git commit -m "message"

$ git push heroku master

</code></pre>

