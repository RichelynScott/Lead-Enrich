import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { InfoIcon } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface AgentToggleProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  pythonBackend: boolean;
  onPythonBackendChange: (checked: boolean) => void;
  fields: { name: string; description: string }[];
}

export function AgentToggle({ checked, onCheckedChange, pythonBackend, onPythonBackendChange, fields }: AgentToggleProps) {
  // Determine if specialized agents would be beneficial
  const specializedFieldPatterns = [
    'company', 'industry', 'employee', 'fund', 'invest', 'valuation',
    'ceo', 'founder', 'executive', 'product', 'service', 'tech',
    'email', 'phone', 'social', 'contact'
  ];

  const fieldNames = fields.map(f => f.name.toLowerCase());
  const fieldDescriptions = fields.map(f => f.description.toLowerCase()).join(' ');
  
  const hasSpecializedFields = specializedFieldPatterns.some(pattern => 
    fieldNames.some(name => name.includes(pattern)) ||
    fieldDescriptions.includes(pattern)
  );

  const recommendedAgents: string[] = [];
  if (fieldNames.some(n => n.includes('company') || n.includes('industry')) ||
      fieldDescriptions.includes('company')) {
    recommendedAgents.push('Company Research');
  }
  if (fieldNames.some(n => n.includes('fund') || n.includes('invest')) ||
      fieldDescriptions.includes('funding')) {
    recommendedAgents.push('Fundraising Intelligence');
  }
  if (fieldNames.some(n => n.includes('ceo') || n.includes('founder')) ||
      fieldDescriptions.includes('leadership')) {
    recommendedAgents.push('People & Leadership');
  }
  if (fieldNames.some(n => n.includes('product') || n.includes('tech')) ||
      fieldDescriptions.includes('product')) {
    recommendedAgents.push('Product & Technology');
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3">
        <Switch
          id="agent-mode"
          checked={checked}
          onCheckedChange={onCheckedChange}
        />
        <Label htmlFor="agent-mode" className="flex items-center gap-2 cursor-pointer">
          Use Specialized Agents
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <InfoIcon className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent className="max-w-sm">
                <div className="space-y-2">
                  <p className="font-semibold">Specialized Agents</p>
                  <p className="text-sm">
                    Enable AI agents that are experts in specific domains like company research, 
                    fundraising, and leadership information.
                  </p>
                  {hasSpecializedFields && recommendedAgents.length > 0 && (
                    <>
                      <p className="text-sm font-medium mt-2">
                        Recommended for your fields:
                      </p>
                      <ul className="text-sm list-disc list-inside">
                        {recommendedAgents.map(agent => (
                          <li key={agent}>{agent}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </Label>
        {hasSpecializedFields && (
          <span className="text-xs text-green-600 font-medium">
            ✨ Recommended
          </span>
        )}
      </div>
      
      <div className="flex items-center space-x-3 pl-4 border-l-2 border-blue-200">
        <Switch
          id="python-backend"
          checked={pythonBackend}
          onCheckedChange={onPythonBackendChange}
        />
        <Label htmlFor="python-backend" className="flex items-center gap-2 cursor-pointer">
          Use Python CrewAI Backend
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <InfoIcon className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent className="max-w-sm">
                <div className="space-y-2">
                  <p className="font-semibold">Advanced Python Backend</p>
                  <p className="text-sm">
                    Uses your advanced CrewAI multi-agent system from the src/ folder with enhanced features:
                  </p>
                  <ul className="text-sm list-disc list-inside">
                    <li>Decision maker validation</li>
                    <li>Enhanced CSV processing</li>
                    <li>Email research capabilities</li>
                    <li>Florida Sunbiz integration</li>
                    <li>Advanced lead enrichment</li>
                  </ul>
                  <p className="text-xs text-amber-600 mt-2">
                    Requires Python server: <code>python -m uvicorn src.api_server:app --reload --port 8000</code>
                  </p>
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </Label>
        <span className="text-xs text-blue-600 font-medium">
          🚀 Advanced
        </span>
      </div>
    </div>
  );
}