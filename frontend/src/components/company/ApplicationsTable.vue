<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  applications: {
    type: Array,
    required: true
  },
  tab: {
    type: String,
    required: true
  }
})

const emit = defineEmits([
  'resume',
  'schedule',
  'status-change'
])

function sendOffer(application) {

  if (application.offer) {

    router.push(
      `/company/offers/${application.offer.id}`
    )

  } else {

    router.push(
      `/company/offers/new/${application.application_id}`
    )

  }

}

function interviewStatus(application) {
  if (!application.interview)
    return 'Not Scheduled'

  return application.interview.status
}

function offerStatus(application) {
  if (!application.offer)
    return 'Not Sent'

  return application.offer.status
}
</script>

<template>

<div class="table-responsive">

<table class="table table-bordered table-hover align-middle">

<thead class="table-dark">

<tr>

<th>Roll No</th>

<th>Name</th>

<th>CGPA</th>

<th>Program</th>

<th>Year</th>

<th v-if="tab=='Shortlisted'">
Interview Status
</th>

<th v-if="tab=='Selected'">
Offer Status
</th>

<th>
Resume
</th>

<th>
Actions
</th>

</tr>

</thead>

<tbody>

<tr
v-for="application in applications"
:key="application.application_id">

<td>

{{ application.roll_no }}

</td>

<td>

{{ application.student_name }}

</td>

<td>

{{ application.cgpa }}

</td>

<td>

{{ application.program_name }}

</td>

<td>

{{ application.year }}

</td>

<td
v-if="tab=='Shortlisted'">

<span
class="badge"
:class="{

'bg-secondary':
!application.interview,

'bg-primary':
application.interview &&
application.interview.status=='Scheduled',

'bg-success':
application.interview &&
application.interview.status=='Completed',

'bg-danger':
application.interview &&
application.interview.status=='Cancelled'

}">

{{ interviewStatus(application) }}

</span>

</td>

<td
v-if="tab=='Selected'">

<span
class="badge"
:class="{

'bg-secondary':
!application.offer,

'bg-warning':
application.offer &&
application.offer.status=='Offered',

'bg-success':
application.offer &&
application.offer.status=='Accepted',

'bg-danger':
application.offer &&
application.offer.status=='Rejected'

}">

{{ offerStatus(application) }}

</span>

</td>

<td>

<button
class="btn btn-outline-primary btn-sm"
@click="emit('resume',application)">

View Resume

</button>

</td>

<td>

<!-- Applied -->

<template
v-if="tab=='Applied'">

<button
class="btn btn-success btn-sm me-2"
@click="emit('status-change',application.application_id,'Shortlisted')">

Shortlist

</button>

<button
class="btn btn-danger btn-sm"
@click="emit('status-change',application.application_id,'Rejected')">

Reject

</button>

</template>

<!-- Shortlisted -->

<template
v-else-if="tab=='Shortlisted'">

<button
class="btn btn-info btn-sm me-2"
@click="emit('schedule',application)">

{{ application.interview ? 'Reschedule' : 'Schedule' }}

</button>

<button
  class="btn btn-success btn-sm me-2"
  :disabled="!application.interview || application.interview.status !== 'Completed'"
  @click="emit('status-change', application.application_id, 'Selected')">
  Select
</button>

<button
class="btn btn-danger btn-sm"
@click="emit('status-change',application.application_id,'Rejected')">

Reject

</button>

</template>

<!-- Selected -->

<template
v-else-if="tab=='Selected'">

<button
class="btn btn-primary btn-sm"
@click="sendOffer(application)">

{{ application.offer ? 'View Offer' : 'Send Offer' }}

</button>

</template>

<!-- Rejected -->

<template
v-else>

<span class="text-muted">

No Actions

</span>

</template>

</td>

</tr>

<tr
v-if="applications.length===0">

<td
:colspan="tab=='Applied' || tab=='Rejected' ? 7 : 8"
class="text-center text-muted">

No applications found.

</td>

</tr>

</tbody>

</table>

</div>

</template>