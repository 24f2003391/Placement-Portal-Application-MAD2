<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

import DriveInfoCard from '@/components/company/DriveInfoCard.vue'
import EligibilityTable from '@/components/company/EligibilityTable.vue'
import InterviewTable from '@/components/company/InterviewTable.vue'
import ApplicationsTable from '@/components/company/ApplicationsTable.vue'
import ScheduleInterviewModal from '@/components/company/ScheduleInterviewModal.vue'
import DocumentViewer from '@/components/DocumentViewer.vue'

const route = useRoute()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const drive = ref({
  eligibility: [],
  interviews: [],
  summary: {
    Applied: 0,
    Shortlisted: 0,
    Selected: 0,
    Rejected: 0,
    'Upcoming Interviews': 0
  }
})

const applications = ref({
  Applied: [],
  Shortlisted: [],
  Selected: [],
  Rejected: []
})

const activeTab = ref('Applied')

const showInterviewModal = ref(false)
const selectedApplication = ref(null)

const showResume = ref(false)
const resumeUrl = ref('')
const resumeTitle = ref('')
const resumeDetails = ref({})

const currentApplications = computed(() => {
  return applications.value[activeTab.value] || []
})

async function fetchDrive() {
  loading.value = true

  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/company/drives/${route.params.id}`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    drive.value = data
  } catch (err) {
    console.error(err)
    messageStore.updateMessages(
      'Unable to fetch drive details.',
      'danger'
    )
  } finally {
    loading.value = false
  }
}

async function fetchApplications() {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/company/drives/${route.params.id}/applications`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    applications.value = data
  } catch (err) {
    console.error(err)
    messageStore.updateMessages(
      'Unable to fetch applications.',
      'danger'
    )
  }
}

async function cancelInterview(interviewId) {
  if (!confirm('Cancel this interview?'))
    return

  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/company/interviews/${interviewId}/cancel`,
      {
        method: 'PUT',
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    messageStore.updateMessages(data.message)

    await fetchDrive()
    await fetchApplications()

  } catch (err) {
    console.error(err)

    messageStore.updateMessages(
      'Unable to cancel interview.',
      'danger'
    )
  }
}

async function completeInterview(interviewId) {
  if (!confirm('Mark this interview as completed?'))
    return

  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/company/interviews/${interviewId}/complete`,
      {
        method: 'PUT',
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    messageStore.updateMessages(data.message)

    await fetchDrive()
    await fetchApplications()

  } catch (err) {
    console.error(err)

    messageStore.updateMessages(
      'Unable to complete interview.',
      'danger'
    )
  }
}

async function updateApplicationStatus(applicationId, status) {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/company/applications/${applicationId}`,
      {
        method: 'PUT',
        headers: {
          Authorization: authStore.token,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    messageStore.updateMessages(data.message)

    await fetchDrive()
    await fetchApplications()
  } catch (err) {
    console.error(err)
  }
}

function openInterviewModal(application) {
  selectedApplication.value = application
  showInterviewModal.value = true
}

function closeInterviewModal() {
  selectedApplication.value = null
  showInterviewModal.value = false
}

async function viewResume(application) {
  showResume.value = true

  resumeTitle.value = `${application.student_name} Resume`

  resumeDetails.value = {
    Student: application.student_name,
    Roll: application.roll_no,
    Program: application.program_name,
    CGPA: application.cgpa,
    Year: application.year
  }

  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/company/applications/${application.application_id}/resume`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    if (!res.ok) {
      const data = await res.json()
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    const blob = await res.blob()
    resumeUrl.value = URL.createObjectURL(blob)
  } catch (err) {
    console.error(err)
    messageStore.updateMessages(
      'Unable to load resume.',
      'danger'
    )
  }
}

function closeResume() {
    if (resumeUrl.value)
    URL.revokeObjectURL(resumeUrl.value)
  showResume.value = false
  resumeUrl.value = ''
}

async function interviewScheduled() {
  closeInterviewModal()
  await fetchDrive()
  await fetchApplications()
}

onMounted(async () => {
  await fetchDrive()
  await fetchApplications()
})
</script>

<template>
  <div class="container mt-4">

    <div
      v-if="loading"
      class="text-center my-5">
      <div class="spinner-border"></div>
    </div>

    <template v-else>

      <h2 class="mb-4">
        {{ drive.job_title }}
      </h2>

      <DriveInfoCard
        :drive="drive"
      />

      <EligibilityTable
        :eligibility="drive.eligibility"
      />

      <InterviewTable
    :interviews="drive.interviews"
    @cancel="cancelInterview"
    @complete="completeInterview"
/>

      <h4 class="mt-5 mb-3">
        Applications
      </h4>

      <ul class="nav nav-tabs mb-3">
        <li
          class="nav-item"
          v-for="tab in ['Applied','Shortlisted','Selected','Rejected']"
          :key="tab">

          <button
            class="nav-link"
            :class="{ active: activeTab === tab }"
            @click="activeTab = tab">

            {{ tab }}

            <span class="badge bg-secondary ms-2">
              {{ drive.summary?.[tab] ?? 0 }}
            </span>

          </button>

        </li>
      </ul>

      <ApplicationsTable
        :applications="currentApplications"
        :tab="activeTab"
        @resume="viewResume"
        @schedule="openInterviewModal"
        @status-change="updateApplicationStatus"
      />

    </template>

    <ScheduleInterviewModal
      :show="showInterviewModal"
      :application="selectedApplication"
      @close="closeInterviewModal"
      @scheduled="interviewScheduled"
    />

    <DocumentViewer
      :show="showResume"
      :title="resumeTitle"
      :pdfUrl="resumeUrl"
      :details="resumeDetails"
      @close="closeResume"
    />

  </div>
</template>