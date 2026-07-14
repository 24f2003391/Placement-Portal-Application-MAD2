<script setup>
defineProps({
  drive: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="card mb-4">

    <div class="card-header">
      <h4 class="mb-0">
        Drive Details
      </h4>
    </div>

    <div class="card-body">

      <div class="row mb-3">

        <div class="col-md-6">
          <strong>Job Title</strong>
          <p>{{ drive.job_title }}</p>
        </div>

        <div class="col-md-6">
          <strong>Status</strong><br>

          <span
            class="badge"
            :class="{
              'bg-warning text-dark': drive.status === 'Pending',
              'bg-success': drive.status === 'Approved',
              'bg-danger': drive.status === 'Rejected',
              'bg-secondary': drive.status === 'Closed'
            }"
          >
            {{ drive.status }}
          </span>

        </div>

      </div>

      <div class="row mb-3">

        <div class="col-md-6">
          <strong>Application Deadline</strong>
          <p>{{ drive.application_deadline }}</p>
        </div>

      </div>

      <div class="mb-4">

        <strong>Job Description</strong>

        <div class="border rounded p-3 bg-light mt-2">
          {{ drive.job_description }}
        </div>

      </div>

      <hr>

      <div class="row text-center">

        <div class="col">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5>{{ drive.summary.Applied }}</h5>
              <small>Applied</small>
            </div>
          </div>
        </div>

        <div class="col">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h5>{{ drive.summary.Shortlisted }}</h5>
              <small>Shortlisted</small>
            </div>
          </div>
        </div>

        <div class="col">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5>{{ drive.summary.Selected }}</h5>
              <small>Selected</small>
            </div>
          </div>
        </div>

        <div class="col">
          <div class="card bg-danger text-white">
            <div class="card-body">
              <h5>{{ drive.summary.Rejected }}</h5>
              <small>Rejected</small>
            </div>
          </div>
        </div>

        <div class="col">
          <div class="card bg-dark text-white">
            <div class="card-body">
              <h5>{{ drive.summary['Upcoming Interviews'] }}</h5>
              <small>Upcoming Interviews</small>
            </div>
          </div>
        </div>

      </div>

    </div>

  </div>
</template>