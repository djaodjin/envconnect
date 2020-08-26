import {
  RestSerializer,
  Server,
  Model,
  Factory,
  hasMany,
  belongsTo,
  trait,
  association,
} from 'miragejs'
import faker from 'faker'
import snakeCase from 'lodash/snakeCase'

import {
  NUM_BENCHMARKS,
  BENCHMARK_MAX_COMPANIES,
  INDUSTRY_SECTIONS,
} from './config'
import industries from './fixtures/industries'
import previousIndustries from './fixtures/previousIndustries'
import scenarios from './scenarios'
import {
  DEFAULT_ASSESSMENT_STEP,
  MAP_QUESTION_FORM_TYPES,
  PRACTICE_VALUES,
  STEP_FREEZE_KEY,
  VALID_ASSESSMENT_STEPS,
  VALID_ASSESSMENT_TARGETS_KEYS,
  VALID_QUESTION_TYPES,
} from '../config/app'
import { getRandomInt } from '../common/utils'

const MIN_PRACTICE_VALUE = PRACTICE_VALUES[0].value
const MAX_PRACTICE_VALUE = PRACTICE_VALUES[PRACTICE_VALUES.length - 1].value

const ApplicationSerializer = RestSerializer.extend({
  keyForAttribute(attr) {
    return snakeCase(attr)
  },
})

// Setting faker seed to get consistent results
faker.seed(582020)

export function makeServer({ environment = 'development', apiBasePath }) {
  return new Server({
    environment,

    fixtures: {
      industries,
      previousIndustries,
    },

    models: {
      answer: Model.extend({
        organization: belongsTo(),
        assessment: belongsTo(),
        question: belongsTo(),
      }),
      assessment: Model.extend({
        targets: hasMany(),
        practices: hasMany(),
        score: belongsTo(),
      }),
      benchmark: Model,
      industry: Model,
      organization: Model.extend({
        assessments: hasMany(),
      }),
      organizationGroup: Model.extend({
        organizations: hasMany(),
      }),
      practice: Model.extend({
        question: belongsTo(),
      }),
      previousIndustry: Model,
      question: Model.extend({
        practice: belongsTo(),
      }),
      score: Model.extend({
        benchmarks: hasMany(),
      }),
      shareEntry: Model.extend({
        organization: belongsTo(),
      }),
      target: Model,
    },

    factories: {
      assessment: Factory.extend({
        campaign() {
          return 'assessment'
        },
        created_at() {
          return faker.date.past()
        },
        is_frozen() {
          return false
        },
        status() {
          return DEFAULT_ASSESSMENT_STEP
        },
        afterCreate(assessment) {
          assessment.update({ slug: assessment.id })
        },
      }),

      answer: Factory.extend({
        metric() {
          return null
        },
        unit() {
          return null
        },
        measured() {
          return null
        },
        created_at() {
          return null
        },
        collected_by() {
          return null
        },
        author() {
          return 'current_user@testmail.com'
        },
        // TODO: Remove
        // answers() {
        //   const questionForm = MAP_QUESTION_FORM_TYPES[this.question.type]
        //   const options = questionForm.options.map((o) => o.value)

        //   if (questionForm.name === 'FormQuestionTextarea') {
        //     return [faker.lorem.paragraph()]
        //   }
        //   if (questionForm.name === 'FormQuestionQuantity') {
        //     return [faker.random.number(), faker.random.arrayElement(options)]
        //   }
        //   // Smaller chance of showing a comment
        //   const comment = Math.random() > 0.8 ? faker.lorem.sentences(3) : ''
        //   return [faker.random.arrayElement(options), comment]
        // },
        // answered() {
        //   return true
        // },

        // Current answers won't have a frozen date
        isPrevious: trait({
          author() {
            return faker.internet.email()
          },
          frozen() {
            return faker.date.past()
          },
        }),
      }),

      benchmark: Factory.extend({
        section() {
          return faker.random.arrayElement(INDUSTRY_SECTIONS)
        },
        scores() {
          return [
            {
              label: '0 - 25%', // optional
              value: getRandomInt(0, BENCHMARK_MAX_COMPANIES),
            },
            {
              label: '25% - 50%', // optional
              value: getRandomInt(0, BENCHMARK_MAX_COMPANIES),
            },
            {
              label: '50% - 75%', // optional
              value: getRandomInt(0, BENCHMARK_MAX_COMPANIES),
            },
            {
              label: '75% - 100%', // optional
              value: getRandomInt(0, BENCHMARK_MAX_COMPANIES),
            },
          ]
        },
        coefficient() {
          return 0.1
        },
        companyScore() {
          return getRandomInt(10, 100)
        },
      }),

      organization: Factory.extend({
        slug() {
          return this.id
        },
        printable_name() {
          return faker.random.words(2)
        },
      }),

      organizationGroup: Factory.extend({
        name() {
          return faker.random.word().toUpperCase()
        },
      }),

      practice: Factory.extend({
        question: association(),

        averageValue() {
          return getRandomInt(MIN_PRACTICE_VALUE, MAX_PRACTICE_VALUE + 1)
        },
        environmentalValue() {
          return getRandomInt(MIN_PRACTICE_VALUE, MAX_PRACTICE_VALUE + 1)
        },
        financialValue() {
          return getRandomInt(MIN_PRACTICE_VALUE, MAX_PRACTICE_VALUE + 1)
        },
        operationalValue() {
          return getRandomInt(MIN_PRACTICE_VALUE, MAX_PRACTICE_VALUE + 1)
        },
        implementationRate() {
          return getRandomInt(10, 95)
        },
      }),

      question: Factory.extend({
        section() {
          return faker.random.arrayElement(INDUSTRY_SECTIONS)
        },
        subcategory() {
          return faker.random.arrayElement(this.section.subcategories)
        },
        path() {
          return this.subcategory.path
        },
        text() {
          return faker.lorem.sentence()
        },
        type() {
          return faker.random.arrayElement(VALID_QUESTION_TYPES)
        },
      }),

      score: Factory.extend({
        top() {
          return getRandomInt(80, 95)
        },
        own() {
          return getRandomInt(60, 80)
        },
        average() {
          return getRandomInt(60, 80)
        },
        isValid() {
          return faker.random.boolean()
        },
      }),

      shareEntry: Factory.extend({
        date() {
          return faker.date.past()
        },
      }),

      target: Factory.extend({
        text() {
          return faker.lorem.sentence()
        },
      }),
    },

    serializers: {
      application: ApplicationSerializer,
      assessment: ApplicationSerializer.extend({
        include: ['targets', 'practices'],
      }),
      organization: ApplicationSerializer.extend({
        include: ['assessments'],
      }),
      organizationGroup: ApplicationSerializer.extend({
        include: ['organizations'],
      }),
      practice: ApplicationSerializer.extend({
        include: ['question'],
      }),
      score: ApplicationSerializer.extend({
        include: ['benchmarks'],
      }),
      shareEntry: ApplicationSerializer.extend({
        include: ['organization'],
      }),
    },

    seeds(server) {
      server.loadFixtures()

      scenarios.createOrgEmpty(server, 'empty')
      scenarios.createOrgAssessmentEmpty(server, 'alpha')
      scenarios.createOrgAssessmentOneAnswer(server, 'beta')
    },

    routes() {
      this.namespace = apiBasePath

      this.get('/content', (schema) => {
        const industries = schema.industries.all()
        return {
          count: industries.length,
          next: null,
          previous: null,
          results: industries.models,
        }
      })

      /* --- ORGANIZATIONS --- */
      this.get('/organizations', (schema) => {
        return schema.organizationGroups.all()
      })

      this.get('/profile/:organizationId', (schema, request) => {
        const { organizationId } = request.params
        const organization = schema.organizations.find(organizationId)
        return {
          slug: organization.slug,
          printable_name: organization.printable_name,
        }
      })

      this.get('/:organizationId/sample/', (schema, request) => {
        const { organizationId } = request.params
        const organization = schema.organizations.find(organizationId)
        if (organization.assessments.length) {
          const {
            slug,
            created_at,
            campaign,
          } = organization.assessments.models[0]
          return { campaign, created_at, slug }
        }
        return {}
      })

      /* --- ASSESSMENTS --- */
      this.get('/:organizationId/sample/:assessmentId/', (schema, request) => {
        const { organizationId, assessmentId } = request.params
        const organization = schema.organizations.find(organizationId)
        if (organization.assessments.length) {
          const assessment = organization.assessments.models.find(
            (assessment) => assessment.slug === assessmentId
          )
          const { campaign, created_at, is_frozen, slug } = assessment
          return { campaign, created_at, is_frozen, slug }
        }
        return new Response(404, {}, { errors: ['assessment not found'] })
      })

      this.get(
        '/:organizationId/sample/:assessmentId/answers/',
        (schema, request) => {
          const { organizationId, assessmentId } = request.params
          const answers = schema.answers.where({
            organizationId,
            assessmentId,
          })
          const results = answers.models.map(
            ({
              metric,
              unit,
              measured,
              created_at,
              collected_by,
              question: { path },
            }) => ({
              metric,
              unit,
              measured,
              created_at,
              collected_by,
              question: {
                path,
              },
            })
          )
          return {
            count: results.length,
            next: null,
            previous: null,
            results,
          }
        }
      )

      // TODO: Remove
      this.get('/answers/:organizationId/:assessmentId', (schema, request) => {
        const { organizationId, assessmentId } = request.params
        return schema.answers.where({
          organizationId,
          assessmentId,
        })
      })

      this.get('/assessments/:id')

      this.get('/practices/:organizationId/:assessmentId', (schema) => {
        return schema.practices.all()
      })

      this.get('/previous-industries', (schema) => {
        const previousIndustries = schema.previousIndustries.all()
        return {
          count: previousIndustries.length,
          next: null,
          previous: null,
          results: previousIndustries.models,
        }
      })

      this.get('/questions/:organizationId/:assessmentId', (schema) => {
        return schema.questions.all()
      })

      this.get('/score/:organizationId/:assessmentId', (schema) => {
        return schema.scores.find('1')
      })

      this.get('/share-history/:organizationId/:assessmentId', (schema) => {
        return schema.shareEntries.all()
      })

      this.patch('/assessments/:id', (schema, request) => {
        const { id } = request.params
        const properties = JSON.parse(request.requestBody)
        const assessment = schema.assessments.find(id)
        assessment.update(properties)
        return assessment
      })

      this.post('/:organizationId/sample/', (schema, request) => {
        const { organizationId } = request.params
        const attrs = JSON.parse(request.requestBody)
        const newAssessment = this.create('assessment', attrs)
        const organization = schema.organizations.find(organizationId)
        organization.assessments.add(newAssessment)
        const { campaign, created_at, slug } = newAssessment
        return { campaign, created_at, slug }
      })

      this.post('/targets/:organizationId/:assessmentId', (schema, request) => {
        const { assessmentId } = request.params
        const targets = JSON.parse(request.requestBody)

        const assessment = schema.assessments.find(assessmentId)
        targets.forEach((target) => {
          const { id, ...attrs } = target
          if (assessment.targetIds.includes(id)) {
            // update target
            schema.targets.find(id).update(attrs)
          } else {
            // create target
            const newTarget = this.create('target', attrs)
            assessment.targets.add(newTarget)
          }
        })
        return assessment
      })

      this.put(
        '/answer/:organizationId/:assessmentId/:questionId',
        (schema, request) => {
          const { organizationId, assessmentId, questionId } = request.params
          const { id, ...attrs } = JSON.parse(request.requestBody)

          const organization = schema.organizations.find(organizationId)
          const assessment = schema.assessments.find(assessmentId)
          const question = schema.questions.find(questionId)

          let answer = schema.answers.find(id)
          if (answer) {
            answer.update({
              ...attrs,
              organization,
              assessment,
              question,
            })
          } else {
            answer = this.create('answer', {
              ...attrs,
              organization,
              assessment,
              question,
            })
          }
          return answer
        }
      )
    },
  })
}
