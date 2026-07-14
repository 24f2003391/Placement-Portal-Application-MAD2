<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const route = useRoute()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)
const processing = ref(false)

const application = ref({})
const interview = ref(null)
const offer = ref(null)

async function fetchApplication() {

  loading.value = true

  try {

    const res = await fetch(
      `http://127.0.0.1:5000/api/student/applications/${route.params.id}`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message || 'Unable to load application.',
        'danger'
      )

      return

    }

    application.value = data.application
    interview.value = data.interview
    offer.value = data.offer

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

function downloadOffer() {

  window.open(
    `http://127.0.0.1:5000/api/student/offers/${offer.value.id}/download`,
    '_blank'
  )

}

async function updateOffer(action) {

  processing.value = true

  try {

    const res = await fetch(
      `http://127.0.0.1:5000/api/student/offers/${offer.value.id}/${action}`,
      {
        method: 'POST',
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message,
        'danger'
      )

      return

    }

    messageStore.updateMessages(
      data.message,
      'success'
    )

    fetchApplication()

  } catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  } finally {

    processing.value = false

  }

}

function acceptOffer() {
  updateOffer('accept')
}

function rejectOffer() {
  updateOffer('reject')
}

onMounted(fetchApplication)
</script>

<template>

<div class="container mt-4">

  <div
    v-if="loading"
    class="text-center mt-5">

    <div class="spinner-border"></div>

  </div>

  <template v-else>

    <div class="card shadow-sm">

      <div class="card-header">

        <h3>

          {{ application.company }}

        </h3>

        <div class="text-muted">

          {{ application.job_title }}

        </div>

      </div>

      <div class="card-body">

        <h5>

          Application Details

        </h5>

        <table class="table">

          <tbody>

            <tr>

              <th width="220">

                Applied On

              </th>

              <td>

                {{ application.application_date }}

              </td>

            </tr>

            <tr>

              <th>

                Status

              </th>

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

            </tr>

          </tbody>

        </table>

        <hr>

        <h5>

          Interview

        </h5>

        <template v-if="interview">

          <table class="table">

            <tbody>

              <tr>

                <th width="220">

                  Status

                </th>

                <td>

                  {{ interview.status }}

                </td>

              </tr>

              <tr>

                <th>

                  Date & Time

                </th>

                <td>

                  {{ interview.datetime }}

                </td>

              </tr>

              <tr>

                <th>

                  Details

                </th>

                <td>

                  {{ interview.details }}

                </td>

              </tr>

            </tbody>

          </table>

        </template>

        <div
          v-else
          class="text-muted">

          No interview has been scheduled.

        </div>

        <hr>

        <h5>

  Offer

</h5>

<template v-if="offer">

  <table class="table">

    <tbody>

      <tr>

        <th width="220">

          Job Role

        </th>

        <td>

          {{ offer.job_role }}

        </td>

      </tr>

      <tr>

        <th>

          Package

        </th>

        <td>

          {{ offer.package }}

        </td>

      </tr>

      <tr>

        <th>

          Joining Date

        </th>

        <td>

          {{ offer.joining_date }}

        </td>

      </tr>

      <tr>

        <th>

          Status

        </th>

        <td>

          <span
            class="badge"
            :class="{
              'bg-warning text-dark': offer.status=='Offered',
              'bg-success': offer.status=='Accepted',
              'bg-danger': offer.status=='Rejected'
            }">

            {{ offer.status }}

          </span>

        </td>

      </tr>

    </tbody>

  </table>

  <button
    class="btn btn-primary me-2"
    @click="downloadOffer">

    Download Offer Letter

  </button>

  <template v-if="offer.status=='Offered'">

    <button
      class="btn btn-success me-2"
      :disabled="processing"
      @click="acceptOffer">

      Accept Offer

    </button>

    <button
      class="btn btn-danger"
      :disabled="processing"
      @click="rejectOffer">

      Reject Offer

    </button>

  </template>

</template>

<div
  v-else
  class="text-muted">

  No offer has been issued yet.

</div>

      </div>

    </div>

  </template>

</div>

</template>