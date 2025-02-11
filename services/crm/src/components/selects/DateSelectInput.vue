<script setup lang="ts">
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import { computed, ref } from "vue";
import DateCalendar from "@/components/DateCalendar.vue";
import * as parser from "@/parser";

const props = defineProps({
	error: {
		type: String,
	},
	placeholder: {
		type: String,
	},
	value: {
		type: String,
		required: true,
	},
	required: {
		type: Boolean,
		default: false,
	},
	readonly: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "submit", value: string): void;
	(e: "close"): void;
}>();

const active = ref(false);
const value = computed(() => {
	if (!props.value) {
		return "";
	}
	return props.value;
});
const dateToString = (date: Date) => {
	return parser.formatDate(date.toDateString()).cellLines[0].value;
};
const date = computed(() => {
	if (!props.value) return;

	if (!parser.validateFormattedDate(props.value)) return;

	return parser.formattedDateToDate(props.value);
});

const focusOut = () => {
	active.value = false;

	emits("close");
};
const submit = (val: Date) => {
	emits("submit", dateToString(val));
};
</script>

<template>
	<div class="msi-wrapper" @focusin="active = true" @focusout="focusOut">
		<MaybeDelayInput
			class="msi-input"
			:value="value"
			@submit="(val: string) => emits('submit', val)"
			:error="props.error"
			:placeholder="props.placeholder"
			:with-search-icon="false"
			:with-edit-mark="true"
			:error-left-align="true"
			:required="props.required"
			:readonly="props.readonly"
		></MaybeDelayInput>
		<Transition name="fade">
			<DateCalendar
				class="calendar"
				v-if="active"
				:date="date"
				@pointerdown.prevent
				@submit="submit"
			></DateCalendar>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.msi-wrapper {
	display: flex;
	flex-direction: column;
	position: relative;

	.msi-input {
		width: 100%;
		height: 48px;
	}
	.calendar {
		position: absolute;
		top: 48px;
	}
}
</style>
