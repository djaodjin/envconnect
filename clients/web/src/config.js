import FormQuestion from './common/FormQuestion'

const FormQuestionRadioDiscrete = new FormQuestion('FormQuestionRadio', [
  {
    text: 'Yes',
    value: 'yes',
  },
  {
    text: 'No',
    value: 'no',
  },
])
FormQuestionRadioDiscrete.render = function (answerObj) {
  const selected = this.options.find((opt) => opt.value === answerObj.answer)
  return selected.text
}

const FormQuestionRadioRange = new FormQuestion('FormQuestionRadio', [
  {
    text: 'Yes',
    value: 'yes',
  },
  {
    text: 'Mostly Yes',
    value: 'most-yes',
  },
  {
    text: 'Mostly No',
    value: 'most-no',
  },
  {
    text: 'No',
    value: 'no',
  },
  {
    text: 'Not Applicable',
    value: 'not-app',
  },
])
FormQuestionRadioRange.render = function (answerObj) {
  const selected = this.options.find((opt) => opt.value === answerObj.answer)
  return selected.text
}

const FormQuestionRadioLabeled = new FormQuestion('FormQuestionRadio', [
  {
    text: "<b class='mr-1'>Initiating:</b>There is minimal management support",
    value: 'initiating',
  },
  {
    text:
      "<b class='mr-1'>Progresssing:</b>Support is visible and clearly demonstrated",
    value: 'progressing',
  },
  {
    text:
      "<b class='mr-1'>Optimizing:</b>Executive management reviews environmental performance, risks and opportunities, and endorses/sets goals",
    value: 'optimizing',
  },
  {
    text:
      "<b class='mr-1'>Leading:</b>The Board of Directors annually reviews environmental performance and sets or endorses goals",
    value: 'leading',
  },
  {
    text:
      "<b class='mr-1'>Transforming:</b>Executive management sponsors transformative change in industry sector and beyond",
    value: 'transforming',
  },
])
FormQuestionRadioLabeled.render = function (answerObj) {
  const selected = this.options.find((opt) => opt.value === answerObj.answer)
  return selected.text
}

const FormQuestionTextarea = new FormQuestion('FormQuestionTextarea')
FormQuestionTextarea.render = function (answerObj) {
  return answerObj.answer
}

const FormQuestionQuantity = new FormQuestion('FormQuestionQuantity', [
  {
    text: 'Kilowatt-hour (kWh) of Electricity  / Year',
    value: 'kwh-year',
  },
  {
    text: 'Metric Tons / Year',
    value: 'tons-year',
  },
  {
    text: 'GHG Emissions',
    value: 'ghg-emissions-generated',
  },
  {
    text: 'US Gallons / Year',
    value: 'gallons-year',
  },
  {
    text: 'mmBtu / Year',
    value: 'mmbtu-year',
  },
  {
    text: 'Cubic meters / Year',
    value: 'm3-year',
  },
  {
    text: 'Kilo liters / Year',
    value: 'kiloliters-year',
  },
  {
    text: 'Cubic feet / Year',
    value: 'ft3-year',
  },
  {
    text: 'Cubic feet / Year',
    value: 'ft3-year',
  },
])
FormQuestionQuantity.render = function (answerObj) {
  const unit = this.options.find((opt) => opt.value === answerObj.unit)
  return `${answerObj.answer} ${unit.text}`
}

export const MAP_QUESTION_FORM_TYPES = {
  1: FormQuestionRadioDiscrete,
  2: FormQuestionRadioRange,
  3: FormQuestionRadioLabeled,
  4: FormQuestionTextarea,
  5: FormQuestionQuantity,
}

export const VALID_QUESTION_TYPES = Object.keys(MAP_QUESTION_FORM_TYPES)
