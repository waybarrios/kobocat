class Question
    constructor: (obj) ->
        @type = obj.type if _(obj).has('type')
        @name = obj.name if _(obj).has('name')
        @label = obj.label if _(obj).has('label')
        @hint = obj.hint if _(obj).has('hint')
        #TODO: construct @choices from children
        choices = {}
        if _(obj).has('children')
            _(obj.children).each (c) -> choices[c.name] = c
        @choices = choices

    getSupportedLanguages : () ->
        return _.keys(@label) if typeof(@label) == 'object'
        
    getLabel : (language) ->
        return @label if typeof(@label) == 'string'
        return @name unless typeof(@label) == 'object'
        if language and @label.hasOwnProperty(language)
            return @label[language]
        else
            return _.values(@label)[0]
    
    getChoices : () ->
        @choices

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
            if question.type in ["group","repeat"] and question.children
                @parseQuestions(question.children, question.name)
            else
                prefix = if parentQuestionName then parentQuestionName + sep else ""
                question.name = prefix + question.name
                #@questions[question.name] = question
                @questions[question.name] = new Question(question)
        return

    _parseSupportedLanguages : () ->
        @supportedLanguages = _(@questions).chain()
            .map((q) -> return q.getSupportedLanguages())
            .flatten().compact().uniq()
            .value()
    
    getQuestionsOfTypes : (types) ->
        _(@questions).filter (q) -> _(types).find (t) -> t == q.type

    getQuestionsOfType : (type) ->
        _(@questions).filter (q) -> type == q.type
    
    getNumQuestionsOfType : (type) -> (@getQuestionOfType type).length
    getSelectOneQuestions : () -> @getQuestionsOfType "select one"
    getNumSelectOneQuestions : () -> @getNumQuestionsOfType "select one"
    getGeoPointQuestion : () -> @getQuestionsOfTypes(["gps","geopoint"])[0]
    getAllGeoPointQuestions : () -> @getQuestionsOfTypes(["gps","geopoint"])
       
    getQuestionByName: (qName) -> @questions[qName]

# Finally, export the Form and Question Classes
window.Form = Form
window.Question = Question
