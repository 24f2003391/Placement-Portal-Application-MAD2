<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/messageStore'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

const showModal = ref(false)
const loadingResume = ref(false)
const resumeUrl = ref('')

const messageStore = useMessageStore()

const applications = ref([])
const loading = ref(false)

const search = ref({
  drive_id: '',
  student_id: '',
  status: '',
  start_date: '',
  end_date: ''
})

async function viewResume(applicationId) {
  showModal.value = true
  loadingResume.value = true
  resumeUrl.value = ''

  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/admin/applications/${applicationId}/resume`,
      {
        headers: {
          Authorization: `Bearer ${authStore.getAuthToken()}`
        }
      }
    )

    if (!res.ok) {
      const data = await res.json()
      messageStore.updateMessages(data.message || 'Failed to load resume')
      closeModal()
      return
    }

    const blob = await res.blob()
    resumeUrl.value = URL.createObjectURL(blob)

  } catch (err) {
    messageStore.updateMessages('Error loading resume')
    closeModal()
    console.error(err)
  } finally {
    loadingResume.value = false
  }
}

function closeModal() {
  showModal.value = false
  resumeUrl.value = ''
}

// 🔹 Fetch
async function fetchApplications() {
  loading.value = true

  try {
    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })

    const res = await fetch(`http://127.0.0.1:5000/api/admin/applications?${params}`)
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch applications')
      return
    }

    applications.value = data

  } catch (err) {
    messageStore.updateMessages('Error fetching applications')
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchApplications)
</script>

<template>
  <div class="container mt-4">

    <h2 class="mb-3">Applications</h2>

    <!-- 🔍 Search -->
    <div class="row g-2 mb-3">

      <div class="col">
        <input v-model="search.drive_id" class="form-control" placeholder="Drive ID">
      </div>

      <div class="col">
        <input v-model="search.student_id" class="form-control" placeholder="Student Roll No">
      </div>

      <div class="col">
        <input type="date" v-model="search.start_date" class="form-control">
      </div>

      <div class="col">
        <input type="date" v-model="search.end_date" class="form-control">
      </div>

      <div class="col">
        <select v-model="search.status" class="form-select">
          <option value="">All Status</option>
          <option>Applied</option>
          <option>Shortlisted</option>
          <option>Selected</option>
          <option>Rejected</option>
          <option>Cancelled</option>
        </select>
      </div>

      <div class="col">
        <button class="btn btn-primary w-100" @click="fetchApplications">
          Search
        </button>
      </div>

    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center">
      Loading...
    </div>

    <!-- Table -->
    <table v-if="!loading" class="table table-bordered table-hover">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Drive ID</th>
          <th>Job Title</th>
          <th>Student Roll</th>
          <th>Student Name</th>
          <th>Application Date</th>
          <th>Status</th>
          <th>Details</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="a in applications" :key="a.id">
          <td>{{ a.id }}</td>
          <td>{{ a.drive_id }}</td>
          <td>{{ a.job_title }}</td>
          <td>{{ a.student_roll_no }}</td>
          <td>{{ a.student_name }}</td>
          <td>{{ a.application_date }}</td>

          <td>
            <span :class="{
              'badge bg-warning text-dark': a.status === 'Applied',
              'badge bg-info': a.status === 'Shortlisted',
              'badge bg-success': a.status === 'Selected',
              'badge bg-danger': a.status === 'Rejected',
              'badge bg-secondary': a.status === 'Cancelled'
            }">
              {{ a.status }}
            </span>
          </td>

          <!-- View Details -->
          <td>
            <button class="btn btn-info btn-sm"
                :disabled="loadingResume"
                @click="viewResume(a.id)">
                View
            </button>
          </td>

        </tr>
      </tbody>
    </table>
    <!-- Resume Modal -->
    <div v-if="showModal">
    
        <!-- backdrop -->
        <div class="modal-backdrop fade show"></div>

        <div class="modal fade show d-block" tabindex="-1">
            <div class="modal-dialog modal-xl">
            <div class="modal-content">

                <!-- Header -->
                <div class="modal-header">
                <h5 class="modal-title">Student Resume</h5>
                <button class="btn-close" @click="closeModal"></button>
                </div>

                <!-- Body -->
                <div class="modal-body">

                <!-- Loading -->
                <div v-if="loadingResume" class="text-center">
                    <div class="spinner-border"></div>
                    <p class="mt-2">Loading resume...</p>
                </div>

                <!-- PDF Preview -->
                <iframe
                    v-else-if="resumeUrl"
                    :src="resumeUrl"
                    width="100%"
                    height="500px"
                    style="border: none;"
                ></iframe>

                <!-- Error fallback -->
                <div v-else class="text-center text-danger">
                    Failed to load resume
                </div>

                </div>

                <!-- Footer -->
                <div class="modal-footer">

                <!-- 🔥 Open in new tab -->
                <a
                    v-if="resumeUrl"
                    :href="resumeUrl"
                    target="_blank"
                    class="btn btn-primary"
                >
                    Open in New Tab
                </a>

                <!-- 🔥 Download -->
                <a
                    v-if="resumeUrl"
                    :href="resumeUrl"
                    download="resume.pdf"
                    class="btn btn-success"
                >
                    Download Resume
                </a>

                <button class="btn btn-secondary" @click="closeModal">
                    Close
                </button>

                </div>

            </div>
        </div>
    </div>
    </div>
  </div>
</template>