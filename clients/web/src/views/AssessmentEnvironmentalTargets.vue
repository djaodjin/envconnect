<template>
  <fragment>
    <header-secondary
      class="container"
      :orgName="organization.name"
      :industryName="assessment.industryName"
      :title="$t('targets.title')"
    />
    <tab-container :tabs="tabs" :xlLeftCol="8" :xlRightCol="4">
      <template v-slot:tab1>
        <tab-header :text="$t('targets.tab1.title')" />
        <div class="targets-container pa-4 pt-sm-2 px-md-8">
          <div v-if="$vuetify.breakpoint.smAndUp">
            <p class="mb-0">{{ $t('targets.tab1.intro') }}</p>
            <button
              class="section-link"
              type="button"
              @click="showBenchmarkingSection"
            >
              See what other organizations in your industry are doing.
            </button>
          </div>
          <div v-else>
            <p class="mb-0" v-html="$t('targets.tab1.intro-xs')" />
          </div>

          <form-environmental-targets
            v-if="Object.keys(assessment).length"
            :organization="organization"
            :assessment="assessment"
            :previousTargets="previousTargets"
          />
        </div>
      </template>
      <template v-slot:tab2>
        <tab-header ref="benchmarkHeader" :text="$t('targets.tab2.title')" />
        <div class="pa-4 pt-sm-2 px-md-8">
          <p>
            {{
              $t('targets.tab2.intro', {
                industryName:
                  assessment.industryName &&
                  assessment.industryName.toLowerCase(),
              })
            }}
          </p>
          <v-container>
            <v-row>
              <v-col
                cols="12"
                sm="6"
                xl="12"
                v-for="(benchmark, index) in benchmarks"
                :key="benchmark.id"
              >
                <chart-practices-implementation
                  :class="[index % 2 ? 'ml-sm-3 ml-md-6' : 'mr-sm-3 mr-md-6']"
                  :section="benchmark.section"
                  :distribution="benchmark.distribution"
                />
              </v-col>
            </v-row>
          </v-container>
        </div>
      </template>
    </tab-container>
    <dialog-confirm
      storageKey="previousTargets"
      title="Previous Targets"
      actionText="Ok, thanks"
      :show="hasPreviousTargets"
    >
      <p>
        Your organization has submitted environmental targets in the past for
        the industry segment selected.
      </p>
      <p>
        Please edit or re-submit the targets from the most recent assessment.
      </p>
    </dialog-confirm>
  </fragment>
</template>

<script>
import { Fragment } from 'vue-fragment'
import API from '@/common/api'
import ChartPracticesImplementation from '@/components/ChartPracticesImplementation'
import DialogConfirm from '@/components/DialogConfirm'
import FormEnvironmentalTargets from '@/components/FormEnvironmentalTargets'
import HeaderSecondary from '@/components/HeaderSecondary'
import TabContainer from '@/components/TabContainer'
import TabHeader from '@/components/TabHeader'

export default {
  name: 'AssessmentEnvironmentalTargets',

  props: ['org', 'id'],

  created() {
    this.fetchData()
  },

  data() {
    return {
      organization: {},
      assessment: {},
      benchmarks: [],
      previousTargets: [],
      tabs: [
        { text: this.$t('targets.tab1.title'), href: 'tab-1' },
        { text: this.$t('targets.tab2.title'), href: 'tab-2' },
      ],
      tab: null,
    }
  },

  computed: {
    hasPreviousTargets() {
      return !!this.previousTargets.length
    },
  },

  methods: {
    async fetchData() {
      const [organization, assessment] = await Promise.all([
        this.$context.getOrganization(this.org),
        this.$context.getAssessment(this.org, this.id),
      ])
      const [previousTargets, benchmarks] = await Promise.all([
        API.getPreviousTargets(this.org, assessment),
        API.getBenchmarks(this.org, this.id, assessment.industryPath),
      ])
      this.organization = organization
      this.assessment = assessment
      this.previousTargets = previousTargets
      this.benchmarks = benchmarks[1]
    },
    showBenchmarkingSection() {
      const { top } = this.$refs.benchmarkHeader.$el.getBoundingClientRect()
      document.documentElement.scrollBy({
        top: top - 70, // account for top nav
        left: 0,
        behavior: 'smooth',
      })
    },
  },

  components: {
    ChartPracticesImplementation,
    DialogConfirm,
    FormEnvironmentalTargets,
    Fragment,
    HeaderSecondary,
    TabContainer,
    TabHeader,
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.targets-container {
  position: relative;

  .section-link {
    color: $primary-color;

    @media #{map-get($display-breakpoints, 'sm-and-up')} {
      position: absolute;
      top: -20px;
      right: 30px;
    }

    &:active,
    &:focus {
      outline: 0 none;
    }
  }
}
</style>
