from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig

analyzer = AnalyzerEngine()
engine = AnonymizerEngine()


def redaction(content):
    results = analyzer.analyze(text=content,
                               entities=["PHONE_NUMBER",
                                         "PERSON", "EMAIL_ADDRESS"],
                               language='en')

    result = engine.anonymize(
        text=content,
        analyzer_results=results,
    )
    print(result.text)
    return result.text
