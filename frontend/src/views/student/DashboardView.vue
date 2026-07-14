<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const student = ref({})
const statistics = ref({})
const applications = ref([])
const interviews = ref([])

async function fetchDashboard() {
  loading.value = true

  try {
    const res = await fetch(
      'http://127.0.0.1:5000/api/student/dashboard',
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(
        data.message || 'Failed to load dashboard',
        'danger'
      )
      return
    }

    student.value = data.student
    statistics.value = data.statistics
    applications.value = data.applications
    interviews.value = data.interviews

  } catch (err) {
    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  } finally {
    loading.value = false
  }
}

function editProfile() {
  router.push('/student/profile')
}

function browseDrives() {
  router.push('/student/placement-drives')
}

function viewApplication(id) {
  router.push(`/student/applications/${id}`)
}

onMounted(fetchDashboard)
</script>

<template>

<div class="container mt-4">

  <div class="d-flex justify-content-between align-items-center mb-4">

    <div>

      <h2>
        Welcome, {{ student.name }}
      </h2>

      <p class="text-muted mb-0">
        Student Dashboard
      </p>

    </div>

    <div>

      <button
        class="btn btn-primary me-2"
        @click="editProfile">

        Edit Profile

      </button>

      <button
        class="btn btn-success"
        @click="browseDrives">

        Browse Placement Drives

      </button>

    </div>

  </div>

  <div
    v-if="loading"
    class="text-center mt-5">

    <div class="spinner-border"></div>

  </div>

  <template v-else>

    <div class="row">

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.total_applications }}</h2>

            <p class="mb-0">

              Applications

            </p>

          </div>

        </div>

      </div>

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.total_interviews }}</h2>

            <p class="mb-0">

              Interviews

            </p>

          </div>

        </div>

      </div>

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.total_offers }}</h2>

            <p class="mb-0">

              Offers

            </p>

          </div>

        </div>

      </div>

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>

              {{ statistics.placed ? 'Yes' : 'No' }}

            </h2>

            <p class="mb-0">

              Placed

            </p>

          </div>

        </div>

      </div>

    </div>

    <div class="card shadow-sm mt-4">

      <div class="card-header">

        <strong>

          My Applications

        </strong>

      </div>

      <div class="card-body">

        <table class="table table-hover align-middle">

          <thead>

            <tr>

              <th>Company</th>
              <th>Job Title</th>
              <th>Applied On</th>
              <th>Status</th>
              <th>Action</th>

            </tr>

          </thead>

          <tbody>

            <tr
              v-for="application in applications"
              :key="application.id">

              <td>{{ application.company }}</td>

              <td>{{ application.job_title }}</td>

              <td>{{ application.application_date }}</td>

              <td>

                <span
                  class="badge"
                  :class="{
                    'bg-primary': application.status=='Applied',
                    'bg-info text-dark': application.status=='Shortlisted',
                    'bg-success': application.status=='Selected',
                    'bg-danger': application.status=='Rejected',
                    'bg-secondary': application.status=='Cancelled'
                  }">

                  {{ application.status }}

                </span>

              </td>

              <td>

                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="viewApplication(application.id)">

                  View

                </button>

              </td>

            </tr>

            <tr v-if="applications.length===0">

              <td
                colspan="5"
                class="text-center">

                No Applications Yet

              </td>

            </tr>

          </tbody>

        </table>

      </div>

    </div>

    <div class="card shadow-sm mt-4">

      <div class="card-header">

        <strong>

          Interviews

        </strong>

      </div>

      <div class="card-body">

        <table class="table table-hover align-middle">

          <thead>

            <tr>

              <th>Company</th>
              <th>Job Title</th>
              <th>Date & Time</th>
              <th>Status</th>
              <th>Action</th>

            </tr>

          </thead>

          <tbody>

            <tr
              v-for="interview in interviews"
              :key="interview.id">

              <td>{{ interview.company }}</td>

              <td>{{ interview.job_title }}</td>

              <td>{{ interview.datetime }}</td>

              <td>

                <span
                  class="badge"
                  :class="{
                    'bg-primary': interview.status=='Scheduled',
                    'bg-success': interview.status=='Completed',
                    'bg-secondary': interview.status=='Cancelled'
                  }">

                  {{ interview.status }}

                </span>

              </td>

              <td>

                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="viewApplication(interview.application_id)">

                  View

                </button>

              </td>

            </tr>

            <tr v-if="interviews.length===0">

              <td
                colspan="5"
                class="text-center">

                No Interviews

              </td>

            </tr>

          </tbody>

        </table>

      </div>

    </div>

  </template>

</div>

</template>