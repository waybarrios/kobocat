class Question
    constructor: (@type, @name, @label, children) ->
        #TODO: construct @choices from children

    getSupportedLanguages : () ->
        if typeof(@label) == 'string'
            return 'default'
        else
            return _.keys(@label)
        
    getLabel : (language) ->
        return @label if typeof(@label) == 'string'
        return @name unless typeof(@label) == 'object'
        if language and @label.hasOwnProperty(language)
            return @label[language]
        else
            return _.values(@label)[0]


class Form
    constructor: (@url, @callback, manualInit=False) ->
        @questions = {}
        @supportedLanguages = {}
        loadFormJSON(@url, @callback) unless manualInit

    loadFormJSON : () ->
        $.getJSON(@url, (data) ->
            @init(data)) # does this work, or is this re-defined?

    init : (data) ->
        @_parseQuestions(data.children)
        @_parseSupportedLanguages()
        @callback.call(this) if @callback

    _parseQuestions : (questionList, parentQuestionName="", sep="/") ->
        for question in questionList
            if question.type == "group" and question.children
                @parseQuestions(question.children, question.name)
            else
                prefix = if parentQuestionName then parentQuestionName + sep else ""
                question.name = prefix + question.name
                #@questions.push(question)
                @questions[question.name] = question
        console.log _.pluck(_.values(@questions), 'type')
        return

    _parseSupportedLanguages : () ->
        _.uniq(_.flatten([q.supportedLanguages() for q in @questions]))
    
    # filterObj can be {"type" : ["type1", "type2"]} or {"name" : "name1"}
    getFilteredQuestions : (whatToFilter, listOfOptions) ->
        q for q in @questions when q[whatToFilter] in listOfOptions
    

    getQuestionsOfTypes : (types) -> 
        q for q in @questions when q.type in types
    getQuestionsOfType : (type) -> @getQuestionsOfTypes [type]
    
    getNumQuestionsOfType : (type) -> (@getQuestionOfType type).length

    getSelectOneQuestions : () -> @getQuestionsOfType "select one"
    getNumSelectOneQuestions : () -> @getNumQuestionsOfType "select one"
    getGeoPointQuestion : () -> @getQuestionsOfTypes(["gps","geopoint"])[0]
       
    getQuestionByName: (qName) -> @questions[qName]

