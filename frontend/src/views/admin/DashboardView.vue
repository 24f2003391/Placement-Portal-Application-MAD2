<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(true)

const dashboard = ref({
  students: {
    total: 0,
    placed: 0,
    placement_rate: 0,
    blacklisted: 0
  },
  companies: {
    total: 0,
    approved: 0,
    pending: 0,
    blacklisted: 0
  },
  drives: {
    approved: 0,
    rejected:0,
    closed:0,
    pending: 0
  },
  applications: {
    total: 0,
    shortlisted: 0,
    selected: 0
  },
  offers: {
    sent: 0,
    accepted: 0,
    rejected: 0,
    acceptance_rate: 0
  }
})

async function fetchDashboard() {
  loading.value = true

  try {
    const res = await fetch('http://127.0.0.1:5000/api/admin/dashboard', {
      headers: {
        Authorization: authStore.token
      }
    })

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to load dashboard', 'danger')
      return
    }

    dashboard.value = data

  } catch (err) {
    console.error(err)
    messageStore.updateMessages('Unable to load dashboard', 'danger')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="container mt-4">

    <h2 class="mb-4">Admin Dashboard</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border"></div>
    </div>

    <div v-else>

      <!-- Students -->
      <h4 class="mb-3">Students</h4>

      <div class="row g-3 mb-4">

        <div class="col-md-3">
          <div class="card text-center border-primary">
            <div class="card-body">
              <h6>Total Students</h6>
              <h2>{{ dashboard.students.total }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-success">
            <div class="card-body">
              <h6>Placed Students</h6>
              <h2>{{ dashboard.students.placed }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-info">
            <div class="card-body">
              <h6>Placement Rate</h6>
              <h2>{{ dashboard.students.placement_rate }}%</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-danger">
            <div class="card-body">
              <h6>Blacklisted Students</h6>
              <h2>{{ dashboard.students.blacklisted }}</h2>
            </div>
          </div>
        </div>

      </div>

      <!-- Companies -->
      <h4 class="mb-3">Companies</h4>

      <div class="row g-3 mb-4">

        <div class="col-md-3">
          <div class="card text-center border-primary">
            <div class="card-body">
              <h6>Total Companies</h6>
              <h2>{{ dashboard.companies.total }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-success">
            <div class="card-body">
              <h6>Approved</h6>
              <h2>{{ dashboard.companies.approved }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-warning">
            <div class="card-body">
              <h6>Pending Approval</h6>
              <h2>{{ dashboard.companies.pending }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-danger">
            <div class="card-body">
              <h6>Blacklisted</h6>
              <h2>{{ dashboard.companies.blacklisted }}</h2>
            </div>
          </div>
        </div>

      </div>

      <!-- Drives & Applications -->
      <div class="row">

        <div class="col-md-6">

          <h4 class="mb-3">Placement Drives</h4>

          <div class="row g-3">

            <div class="row g-3">
  <div class="col-md-3 col-6">
    <div class="card text-center border-success">
      <div class="card-body">
        <h6>Approved Drives</h6>
        <h2>{{ dashboard.drives.approved }}</h2>
      </div>
    </div>
  </div>

  <div class="col-md-3 col-6">
    <div class="card text-center border-danger">
      <div class="card-body">
        <h6>Rejected Drives</h6>
        <h2>{{ dashboard.drives.rejected }}</h2>
      </div>
    </div>
  </div>

  <div class="col-md-3 col-6">
    <div class="card text-center border-secondary">
      <div class="card-body">
        <h6>Closed Drives</h6>
        <h2>{{ dashboard.drives.closed }}</h2>
      </div>
    </div>
  </div>

  <div class="col-md-3 col-6">
    <div class="card text-center border-warning">
      <div class="card-body">
        <h6>Pending Drives</h6>
        <h2>{{ dashboard.drives.pending }}</h2>
      </div>
    </div>
  </div>
</div>

          </div>

        </div>

        <div class="col-md-6">

          <h4 class="mb-3">Applications</h4>

          <div class="row g-3">

            <div class="col-4">
              <div class="card text-center border-primary">
                <div class="card-body">
                  <h6>Total</h6>
                  <h2>{{ dashboard.applications.total }}</h2>
                </div>
              </div>
            </div>

            <div class="col-4">
              <div class="card text-center border-info">
                <div class="card-body">
                  <h6>Shortlisted</h6>
                  <h2>{{ dashboard.applications.shortlisted }}</h2>
                </div>
              </div>
            </div>

            <div class="col-4">
              <div class="card text-center border-success">
                <div class="card-body">
                  <h6>Selected</h6>
                  <h2>{{ dashboard.applications.selected }}</h2>
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>

      <!-- Offers -->
      <h4 class="mt-5 mb-3">Offers</h4>

      <div class="row g-3">

        <div class="col-md-3">
          <div class="card text-center border-primary">
            <div class="card-body">
              <h6>Offers Sent</h6>
              <h2>{{ dashboard.offers.sent }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-success">
            <div class="card-body">
              <h6>Offers Accepted</h6>
              <h2>{{ dashboard.offers.accepted }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-danger">
            <div class="card-body">
              <h6>Offers Rejected</h6>
              <h2>{{ dashboard.offers.rejected }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card text-center border-info">
            <div class="card-body">
              <h6>Acceptance Rate</h6>
              <h2>{{ dashboard.offers.acceptance_rate }}%</h2>
            </div>
          </div>
        </div>

      </div>

    </div>

  </div>
</template>