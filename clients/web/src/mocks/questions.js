import { getRandomInt } from '../common/utils'
import Section from '../common/Section'
import Subcategory from '../common/Subcategory'
import Question from '../common/Question'

const DELAY = 100

// Set IDs to null to generate automatic unique IDs
const sections = [
  new Section('123', 'Governance & Management'),
  new Section('345', 'Engineering & Design'),
  new Section('678', 'Construction'),
]

// Set IDs to null to generate automatic unique IDs
const subcategories = [
  new Subcategory('124', 'Responsibility and Authority'),
  new Subcategory('235', 'Management System Rigor'),
  new Subcategory('346', 'General'),
  new Subcategory('457', 'Material Selection'),
]

function getRandomSection() {
  const index = getRandomInt(0, sections.length)
  return sections[index]
}

function getRandomSubcategory() {
  const index = getRandomInt(0, subcategories.length)
  return subcategories[index]
}

export function getQuestions() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve([
        new Question(
          'qa1',
          sections[0],
          subcategories[0],
          'Suspendisse ultricies, nunc aliquam laoreet pellentesque, odio mi pretium metus, facilisis pulvinar mi sapien in leo?',
          '1',
          'Comments'
        ),
        new Question(
          'qb2',
          sections[0],
          subcategories[0],
          'Aenean faucibus eu lectus ac imperdiet. Sed a nisi ac neque pulvinar venenatis ut vitae purus. Fusce sagittis nunc massa, vel pharetra mi maximus hendrerit. Curabitur diam mi, tristique sit amet diam ut, luctus blandit felis?',
          '2',
          'Please explain how you plan to use the results of the assessment.'
        ),
        new Question(
          'qc3',
          sections[0],
          subcategories[1],
          'Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae?',
          '3',
          'Comments'
        ),
        new Question(
          'qd4',
          sections[0],
          subcategories[0],
          'Etiam sagittis risus sit amet quam iaculis, sit amet finibus mauris laoreet. Praesent faucibus interdum libero, tristique tempor felis dictum non. Suspendisse libero magna, tempus sit amet finibus vel, luctus id purus?',
          '4',
          'Comments'
        ),
        new Question(
          'qe5',
          sections[0],
          subcategories[1],
          'Praesent bibendum, felis in scelerisque porta, lacus mauris elementum neque, non pretium sem sapien eu justo?',
          '5',
          'Comments'
        ),
        new Question(
          'qf6',
          sections[1],
          subcategories[2],
          'Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Duis metus urna, ornare non tortor id, mollis aliquet massa?',
          '1',
          'Comments'
        ),
        new Question(
          'qg7',
          sections[1],
          subcategories[3],
          'Nulla pellentesque tempor euismod. Praesent arcu arcu, ornare id metus sit amet, vehicula varius diam. Curabitur porta, ligula quis scelerisque viverra, enim urna pellentesque ligula, et facilisis mi ex dignissim velit. Suspendisse a nunc pulvinar, faucibus ex id, malesuada ligula. Fusce ornare consectetur enim id eleifend?',
          '2',
          'Please explain how you plan to use the results of the assessment.'
        ),
        new Question(
          'qh8',
          sections[1],
          subcategories[3],
          'Maecenas gravida nunc id nibh volutpat mattis. Vivamus ac sapien et felis egestas vestibulum?',
          '3',
          'Comments'
        ),
        new Question(
          'qi9',
          sections[2],
          subcategories[2],
          'Sed iaculis, est nec lacinia sagittis, nunc neque imperdiet nisi, vitae maximus risus risus vel erat?',
          '4',
          'Comments'
        ),
        new Question(
          'qj10',
          sections[2],
          subcategories[3],
          'Donec nec mi in quam sollicitudin cursus. Proin cursus, augue vel aliquam luctus, lacus tortor faucibus sapien, sed pulvinar magna sapien vel purus?',
          '5',
          'Comments'
        ),
        // new Question(
        //   getRandomSection(),
        //   getRandomSubcategory(),
        //   'Duis metus urna, ornare non tortor id, mollis aliquet massa?',
        //   '1',
        //   'Comments'
        // ),
      ])
    }, DELAY)
  })
}