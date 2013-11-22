# fptbot - IRC bot in python w/ module support.

fptbot is a small open source data management system offering basic
entertainment and collaboration features.

The architecture was built with flexibility in mind and can be extented to
provide all sorts of different features and protocols. Currently, only IRC is
supported but support HTTP is planned.

# Features

## User management

The system maintains a list of accounts, so that registered users can
authenticate with the bot for additional administrative functions. Users can be
authenticated with username/password credentials or based on implicit
information such as IRC network-specific registration services. Additionally, a
simple RBAC concept offers basic authorization.

## Calendaring

A central part of the systems consists of a small calendaring system with
support for calendar, event and contact data. The calendaring datastore provides
an abstract mechanism to store data objects in multiple backends. Data can be
replicated over multiple backends using either one-way or two-way
synchronization. Additionally support for limited un-deletion of data items and
autiding of data manipulation is planned.

Currently supported backends are local databases using SQLAlchemy and Google
services using the Google Data API.

## Topic management

The topic of an IRC channel can be set using a variety of data source, such as
calendars, url grabber, etc. When calendar mode is activated, the topic will be
changed upon new calendar events to provide the latest information for all
channel users.

## URL grabber

The URL grabber collects all sorts of URLs posted to the channel such as
websites, pictures, videos, etc. Using plugings, addtional functions can be
executed, e.g. posting the youtube video name to the channel, pushing new URLs
to twitter, etc.

## Information

The information system provides a flexible way to store simple public
information items like URLs or IP adresses.

## Entertainment

The bot offers various entertainment functions like a quote database, the
posting of random facts, and mini games.

## Calendaring

The IRC subsystem offers a simple command-based interface for managing
calendering data.
