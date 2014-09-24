# IC Maths Timetabler

This web app is built using [Flask](http://flask.pocoo.org/) and hosted at [http://icmathstimetabler.herokuapp.com](http://icmathstimetabler.herokuapp.com) on [Heroku](http://www.heroku.com). In order to run this program locally you will first need the Python packages listed in requirements.txt, which can be installed via

```
pip install -r requirements.txt
```

You will also need a local [redis](http://redis.io/) server running. The web server can then be started by running

```
python run.py
```

### Future Ideas

- Calendar subscriptions (i.e. calendar updates if timetable changes)
- Timetable Presets (e.g. first year, second year + options)
- Option to set alerts before events in settings.
- Staff timetables.
- PDF output.

### To do

- Create unit tests.
- Improve general error checking.
- Improve init code (e.g. setup DB)
- Consider external filesystem (e.g. S3)

---

Thanks to [Chris Sisson](http://wwwf.imperial.ac.uk/~csisson/) for providing the webpages that this program needs to scrape.
