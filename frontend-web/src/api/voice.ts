import { apiRequest } from "./client";
import type { VoiceCommandResponse } from "../types/api";

export async function processVoiceCommand(
    token: string,
    command: string,
    context?: Record<string, unknown>,
    confirmed?: boolean,
): Promise<VoiceCommandResponse> {
    return apiRequest<VoiceCommandResponse>("/voice/command", token, {
        method: "POST",
        body: JSON.stringify({ command, context, confirmed }),
    });
}
