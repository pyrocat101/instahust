# Phantom.js script for weibo access token refresh.
# Use crontab to run this task per 12h. (TTL of an access token is 24h)

webpage = require 'webpage'
fs = require 'fs'

BASE_URL = 'http://instahust.ap01.aws.af.cm/'
LOGIN_URL = "#{BASE_URL}weibo_login"

log = (msg) -> console.log "[#{new Date()}] #{msg}"
read_auth_info = -> JSON.parse fs.read 'auth_info.json'

do_the_auth = (auth_url) ->
  auth_info = read_auth_info()
  auth_page = webpage.create()
  auth_page.onConsoleMessage = (msg) -> log msg
  auth_page.open auth_url, (status) ->
    if status isnt 'success'
      log "Unable to open URL: #{auth_url}"
      phantom.exit()
    else
      log "Auth page loaded correctly."

      auth_page.onLoadFinished = (status) ->
        log "Navigated to #{auth_page.url}"
        if auth_page.url isnt BASE_URL
          log 'Error returning Oauth callback page!'
        phantom.exit()

      auth_btn = auth_page.evaluate (auth_info) ->
        document.querySelector('#userId').value = auth_info.username
        document.querySelector('#passwd').value = auth_info.password
        auth_btn = document.querySelector '[node-type=submit]'
        # click on login button
        evObj = document.createEvent 'Events'
        evObj.initEvent 'click', true, false
        auth_btn.dispatchEvent evObj
      , auth_info
      log 'Clicked login button.'

weibo_login = ->
  login_page = webpage.create()
  log 'Opening weibo_login...'
  login_page.open LOGIN_URL, (status) ->
    if status isnt 'success'
      log "Unable to open URL: #{LOGIN_URL}"
      phantom.exit()
    else
      log "weibo_login loaded correctly."
      auth_url = login_page.evaluate ->
        return document.querySelector('a').href
      log "Retrieved auth_url: #{auth_url}"
      login_page.close()
      do_the_auth(auth_url)

phantom.onError = (msg, trace) ->
  msgStack = ['PHANTOM ERROR: ' + msg]
  if trace
    msgStack.push('TRACE:')
    trace.forEach (t) ->
      msgStack.push " -> #{t.file or t.sourceURL}: #{t.line}#{' (in function ' + t.function + ')' if t.function}"
  console.error msgStack.join '\n'
  phantom.exit()

weibo_login()
