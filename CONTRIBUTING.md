Just follow the coding conventions in the project, which is really just pep8 style, along with my naming scheme.
Also, don't use spaces over tabs.

#Conventions:
1. bin
    *Should only have one module: main.py, which contains the code needed to
    setup and start the server.
2. server_modules
    *Modules directly related to things in the server (the user class, the channel class, etc) should go here,
    prefixed with irc_(name_here).
    *Classes inside the module should have an IRC(name_of_class) prefix. eg: `class IRCUser`, `class IRCConfig`, etc.
    *Try to have one main class per module, unless splitting sections of an object which represents things that
    can also be represented as an object up. An example of this is irc_config, where the main class is IRCConfig
    containing attributes which are sections in the config, which are hidden classes.
3. util_modules
    *Modules which contain utility classes/utility methods should go here. If the utility class/method is directly
    related to the server itself, use the irc_(name) prefix for the module and follow the same class naming
    convention as you would with an irc_ module. Otherwise, don't use a prefix. An example of the kind of
    server-related module that would go here and not in server_modules is something like the quitreason enum class,
    and the random nick generation class, which are both more of utility classes than anything. Really though
    just put server utility classes here if they bloat up the main module they are used in.
